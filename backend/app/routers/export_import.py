# app/routers/export_import.py
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Response
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional, List
from datetime import datetime
from bson import ObjectId
import csv
import io
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from ..middleware.auth_middleware import get_current_verified_user
from ..database import get_database
from ..utils.export_helpers import (
    generate_csv_export, generate_pdf_report, 
    validate_csv_import, process_csv_import
)
from ..utils.exceptions import CustomHTTPException

router = APIRouter(prefix="/transactions", tags=["Export/Import"])

@router.get("/export")
async def export_transactions(
    format: str = "csv",  # csv, pdf, json
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    category_id: Optional[str] = None,
    type: Optional[str] = None,
    include_summary: bool = True,
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Export transactions dalam berbagai format"""
    
    if format not in ["csv", "pdf", "json"]:
        raise CustomHTTPException(
            status_code=400,
            detail="Format harus csv, pdf, atau json",
            error_code="INVALID_FORMAT"
        )
    
    # Build filter query
    filter_query = {"user_id": ObjectId(current_user["id"])}
    
    if date_from and date_to:
        filter_query["date"] = {"$gte": date_from, "$lte": date_to}
    elif date_from:
        filter_query["date"] = {"$gte": date_from}
    elif date_to:
        filter_query["date"] = {"$lte": date_to}
    
    if category_id:
        filter_query["category_id"] = ObjectId(category_id)
    
    if type:
        filter_query["type"] = type
    
    # Get transactions with category info
    pipeline = [
        {"$match": filter_query},
        {
            "$lookup": {
                "from": "categories",
                "localField": "category_id",
                "foreignField": "_id",
                "as": "category"
            }
        },
        {"$unwind": "$category"},
        {"$sort": {"date": -1}}
    ]
    
    transactions = await db.transactions.aggregate(pipeline).to_list(length=None)
    
    if not transactions:
        raise CustomHTTPException(
            status_code=404,
            detail="Tidak ada transaksi yang ditemukan untuk diekspor",
            error_code="NO_TRANSACTIONS_FOUND"
        )
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transactions_{current_user['nama_lengkap'].replace(' ', '_')}_{timestamp}"
    
    if format == "csv":
        return await export_csv(transactions, filename, include_summary, current_user)
    elif format == "pdf":
        return await export_pdf(transactions, filename, include_summary, current_user, filter_query, db)
    else:  # json
        return await export_json(transactions, filename, include_summary, current_user)

@router.post("/import")
async def import_transactions(
    file: UploadFile = File(...),
    validate_only: bool = False,
    auto_categorize: bool = True,
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Import transactions dari CSV file"""
    
    if not file.filename.endswith('.csv'):
        raise CustomHTTPException(
            status_code=400,
            detail="File harus berformat CSV",
            error_code="INVALID_FILE_FORMAT"
        )
    
    # Read file content
    content = await file.read()
    try:
        csv_content = content.decode('utf-8')
    except UnicodeDecodeError:
        raise CustomHTTPException(
            status_code=400,
            detail="File encoding tidak valid. Gunakan UTF-8",
            error_code="INVALID_ENCODING"
        )
    
    # Validate CSV format
    validation_result = await validate_csv_import(csv_content, current_user["id"], db)
    
    if not validation_result["is_valid"]:
        return {
            "success": False,
            "message": "Validasi CSV gagal",
            "errors": validation_result["errors"],
            "valid_rows": validation_result["valid_rows"],
            "total_rows": validation_result["total_rows"]
        }
    
    if validate_only:
        return {
            "success": True,
            "message": "Validasi CSV berhasil",
            "valid_rows": validation_result["valid_rows"],
            "total_rows": validation_result["total_rows"],
            "preview": validation_result["preview"][:5]  # Show first 5 rows
        }
    
    # Process import
    import_result = await process_csv_import(
        csv_content, current_user["id"], auto_categorize, db
    )
    
    return {
        "success": True,
        "message": f"Berhasil mengimpor {import_result['imported_count']} transaksi",
        "imported_count": import_result["imported_count"],
        "skipped_count": import_result["skipped_count"],
        "error_count": import_result["error_count"],
        "details": import_result["details"]
    }

@router.get("/template")
async def download_import_template():
    """Download CSV template untuk import"""
    
    template_data = [
        ["date", "type", "amount", "description", "category_name", "payment_method", "location", "notes", "tags"],
        ["2025-07-05 12:00:00", "pengeluaran", "50000", "Makan siang", "Makanan", "cash", "Kantin kampus", "Makan bersama teman", "makanan,kampus"],
        ["2025-07-05 08:00:00", "pemasukan", "100000", "Uang saku", "Allowance", "transfer", "", "Transfer dari ortu", "allowance"],
        ["2025-07-04 19:00:00", "pengeluaran", "25000", "Transport pulang", "Transportasi", "e-wallet", "", "Ojek online", "transport"]
    ]
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(template_data)
    
    response = Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=lunance_import_template.csv"}
    )
    
    return response

# Helper functions for export
async def export_csv(transactions: List[Dict], filename: str, include_summary: bool, current_user: Dict) -> StreamingResponse:
    """Export to CSV format"""
    
    output = io.StringIO()
    fieldnames = [
        'tanggal', 'tipe', 'jumlah', 'deskripsi', 'kategori', 
        'metode_pembayaran', 'lokasi', 'catatan', 'tags'
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    total_pemasukan = 0
    total_pengeluaran = 0
    
    for trans in transactions:
        writer.writerow({
            'tanggal': trans['date'].strftime('%Y-%m-%d %H:%M:%S'),
            'tipe': trans['type'],
            'jumlah': trans['amount'],
            'deskripsi': trans['description'],
            'kategori': trans['category']['nama_kategori'],
            'metode_pembayaran': trans['payment_method'],
            'lokasi': trans.get('location', ''),
            'catatan': trans.get('notes', ''),
            'tags': ','.join(trans.get('tags', []))
        })
        
        if trans['type'] == 'pemasukan':
            total_pemasukan += trans['amount']
        else:
            total_pengeluaran += trans['amount']
    
    if include_summary:
        writer.writerow({})
        writer.writerow({'tanggal': 'RINGKASAN'})
        writer.writerow({'tanggal': 'Total Pemasukan', 'jumlah': total_pemasukan})
        writer.writerow({'tanggal': 'Total Pengeluaran', 'jumlah': total_pengeluaran})
        writer.writerow({'tanggal': 'Saldo', 'jumlah': total_pemasukan - total_pengeluaran})
    
    response = StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}.csv"}
    )
    
    return response

async def export_pdf(transactions: List[Dict], filename: str, include_summary: bool, 
                    current_user: Dict, filter_query: Dict, db) -> StreamingResponse:
    """Export to PDF format"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center
    )
    
    story.append(Paragraph(f"Laporan Transaksi - {current_user['nama_lengkap']}", title_style))
    story.append(Paragraph(f"Diekspor pada: {datetime.now().strftime('%d %B %Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Summary if requested
    if include_summary:
        total_pemasukan = sum(t['amount'] for t in transactions if t['type'] == 'pemasukan')
        total_pengeluaran = sum(t['amount'] for t in transactions if t['type'] == 'pengeluaran')
        saldo = total_pemasukan - total_pengeluaran
        
        summary_data = [
            ['Ringkasan Transaksi'],
            ['Total Pemasukan', f"Rp {total_pemasukan:,.0f}"],
            ['Total Pengeluaran', f"Rp {total_pengeluaran:,.0f}"],
            ['Saldo', f"Rp {saldo:,.0f}"],
            ['Jumlah Transaksi', str(len(transactions))]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
    
    # Transaction table
    table_data = [['Tanggal', 'Tipe', 'Jumlah', 'Deskripsi', 'Kategori', 'Metode']]
    
    for trans in transactions:
        table_data.append([
            trans['date'].strftime('%d/%m/%Y'),
            trans['type'].title(),
            f"Rp {trans['amount']:,.0f}",
            trans['description'][:30] + '...' if len(trans['description']) > 30 else trans['description'],
            trans['category']['nama_kategori'],
            trans['payment_method']
        ])
    
    transaction_table = Table(table_data, colWidths=[1*inch, 0.8*inch, 1.2*inch, 2*inch, 1.2*inch, 0.8*inch])
    transaction_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8)
    ]))
    
    story.append(Paragraph("Detail Transaksi", styles['Heading2']))
    story.append(transaction_table)
    
    doc.build(story)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}.pdf"}
    )

async def export_json(transactions: List[Dict], filename: str, include_summary: bool, current_user: Dict) -> StreamingResponse:
    """Export to JSON format"""
    
    # Convert ObjectId and datetime to string
    export_data = []
    total_pemasukan = 0
    total_pengeluaran = 0
    
    for trans in transactions:
        export_trans = {
            "id": str(trans["_id"]),
            "tanggal": trans["date"].isoformat(),
            "tipe": trans["type"],
            "jumlah": trans["amount"],
            "deskripsi": trans["description"],
            "kategori": {
                "id": str(trans["category"]["_id"]),
                "nama": trans["category"]["nama_kategori"],
                "icon": trans["category"]["icon"],
                "color": trans["category"]["color"]
            },
            "metode_pembayaran": trans["payment_method"],
            "lokasi": trans.get("location"),
            "catatan": trans.get("notes"),
            "tags": trans.get("tags", []),
            "dibuat_pada": trans["created_at"].isoformat()
        }
        export_data.append(export_trans)
        
        if trans['type'] == 'pemasukan':
            total_pemasukan += trans['amount']
        else:
            total_pengeluaran += trans['amount']
    
    result = {
        "metadata": {
            "exported_by": current_user["nama_lengkap"],
            "exported_at": datetime.now().isoformat(),
            "total_transaksi": len(transactions)
        },
        "transaksi": export_data
    }
    
    if include_summary:
        result["ringkasan"] = {
            "total_pemasukan": total_pemasukan,
            "total_pengeluaran": total_pengeluaran,
            "saldo": total_pemasukan - total_pengeluaran
        }
    
    json_content = json.dumps(result, indent=2, ensure_ascii=False)
    
    return StreamingResponse(
        io.BytesIO(json_content.encode('utf-8')),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}.json"}
    )