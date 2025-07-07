import 'base_model.dart';

class University extends BaseModel {
  final String id;
  final String nama;
  final String kode;
  final String alamat;
  final bool statusAktif;
  final String? website;
  final String? telepon;
  final String? email;
  final DateTime createdAt;
  final DateTime updatedAt;

  const University({
    required this.id,
    required this.nama,
    required this.kode,
    required this.alamat,
    required this.statusAktif,
    this.website,
    this.telepon,
    this.email,
    required this.createdAt,
    required this.updatedAt,
  });

  factory University.fromJson(Map<String, dynamic> json) {
    return University(
      id: json['id'] ?? '',
      nama: json['nama'] ?? '',
      kode: json['kode'] ?? '',
      alamat: json['alamat'] ?? '',
      statusAktif: json['status_aktif'] ?? false,
      website: json['website'],
      telepon: json['telepon'],
      email: json['email'],
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updated_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nama': nama,
      'kode': kode,
      'alamat': alamat,
      'status_aktif': statusAktif,
      'website': website,
      'telepon': telepon,
      'email': email,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  University copyWith({
    String? id,
    String? nama,
    String? kode,
    String? alamat,
    bool? statusAktif,
    String? website,
    String? telepon,
    String? email,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return University(
      id: id ?? this.id,
      nama: nama ?? this.nama,
      kode: kode ?? this.kode,
      alamat: alamat ?? this.alamat,
      statusAktif: statusAktif ?? this.statusAktif,
      website: website ?? this.website,
      telepon: telepon ?? this.telepon,
      email: email ?? this.email,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  List<Object?> get props => [
        id,
        nama,
        kode,
        alamat,
        statusAktif,
        website,
        telepon,
        email,
        createdAt,
        updatedAt,
      ];
}

class Fakultas extends BaseModel {
  final String id;
  final String nama;
  final String kode;
  final String universityId;
  final String? deskripsi;
  final DateTime createdAt;
  final DateTime updatedAt;

  const Fakultas({
    required this.id,
    required this.nama,
    required this.kode,
    required this.universityId,
    this.deskripsi,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Fakultas.fromJson(Map<String, dynamic> json) {
    return Fakultas(
      id: json['id'] ?? '',
      nama: json['nama'] ?? '',
      kode: json['kode'] ?? '',
      universityId: json['university_id'] ?? '',
      deskripsi: json['deskripsi'],
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updated_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nama': nama,
      'kode': kode,
      'university_id': universityId,
      'deskripsi': deskripsi,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  Fakultas copyWith({
    String? id,
    String? nama,
    String? kode,
    String? universityId,
    String? deskripsi,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Fakultas(
      id: id ?? this.id,
      nama: nama ?? this.nama,
      kode: kode ?? this.kode,
      universityId: universityId ?? this.universityId,
      deskripsi: deskripsi ?? this.deskripsi,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  List<Object?> get props => [
        id,
        nama,
        kode,
        universityId,
        deskripsi,
        createdAt,
        updatedAt,
      ];
}

class ProgramStudi extends BaseModel {
  final String id;
  final String nama;
  final String kode;
  final String fakultasId;
  final StudyLevel jenjang;
  final AccreditationGrade? akreditasi;
  final DateTime createdAt;
  final DateTime updatedAt;

  const ProgramStudi({
    required this.id,
    required this.nama,
    required this.kode,
    required this.fakultasId,
    required this.jenjang,
    this.akreditasi,
    required this.createdAt,
    required this.updatedAt,
  });

  factory ProgramStudi.fromJson(Map<String, dynamic> json) {
    return ProgramStudi(
      id: json['id'] ?? '',
      nama: json['nama'] ?? '',
      kode: json['kode'] ?? '',
      fakultasId: json['fakultas_id'] ?? '',
      jenjang: StudyLevel.fromString(json['jenjang'] ?? 'S1'),
      akreditasi: AccreditationGrade.fromString(json['akreditasi']),
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updated_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nama': nama,
      'kode': kode,
      'fakultas_id': fakultasId,
      'jenjang': jenjang.value,
      'akreditasi': akreditasi?.value,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  ProgramStudi copyWith({
    String? id,
    String? nama,
    String? kode,
    String? fakultasId,
    StudyLevel? jenjang,
    AccreditationGrade? akreditasi,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return ProgramStudi(
      id: id ?? this.id,
      nama: nama ?? this.nama,
      kode: kode ?? this.kode,
      fakultasId: fakultasId ?? this.fakultasId,
      jenjang: jenjang ?? this.jenjang,
      akreditasi: akreditasi ?? this.akreditasi,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  List<Object?> get props => [
        id,
        nama,
        kode,
        fakultasId,
        jenjang,
        akreditasi,
        createdAt,
        updatedAt,
      ];
}

class UniversityRequest extends BaseModel {
  final String id;
  final String namaUniversity;
  final String kodeUniversity;
  final String alamatUniversity;
  final String? websiteUniversity;
  final String namaPemohon;
  final String email;
  final String nim;
  final RequestStatus status;
  final String? catatanAdmin;
  final DateTime? processedAt;
  final String? processedBy;
  final DateTime createdAt;
  final DateTime updatedAt;

  const UniversityRequest({
    required this.id,
    required this.namaUniversity,
    required this.kodeUniversity,
    required this.alamatUniversity,
    this.websiteUniversity,
    required this.namaPemohon,
    required this.email,
    required this.nim,
    required this.status,
    this.catatanAdmin,
    this.processedAt,
    this.processedBy,
    required this.createdAt,
    required this.updatedAt,
  });

  factory UniversityRequest.fromJson(Map<String, dynamic> json) {
    return UniversityRequest(
      id: json['id'] ?? '',
      namaUniversity: json['nama_university'] ?? '',
      kodeUniversity: json['kode_university'] ?? '',
      alamatUniversity: json['alamat_university'] ?? '',
      websiteUniversity: json['website_university'],
      namaPemohon: json['nama_pemohon'] ?? '',
      email: json['email'] ?? '',
      nim: json['nim'] ?? '',
      status: RequestStatus.fromString(json['status'] ?? 'pending'),
      catatanAdmin: json['catatan_admin'],
      processedAt: json['processed_at'] != null
          ? DateTime.parse(json['processed_at'])
          : null,
      processedBy: json['processed_by'],
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updated_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nama_university': namaUniversity,
      'kode_university': kodeUniversity,
      'alamat_university': alamatUniversity,
      'website_university': websiteUniversity,
      'nama_pemohon': namaPemohon,
      'email': email,
      'nim': nim,
      'status': status.value,
      'catatan_admin': catatanAdmin,
      'processed_at': processedAt?.toIso8601String(),
      'processed_by': processedBy,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  UniversityRequest copyWith({
    String? id,
    String? namaUniversity,
    String? kodeUniversity,
    String? alamatUniversity,
    String? websiteUniversity,
    String? namaPemohon,
    String? email,
    String? nim,
    RequestStatus? status,
    String? catatanAdmin,
    DateTime? processedAt,
    String? processedBy,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return UniversityRequest(
      id: id ?? this.id,
      namaUniversity: namaUniversity ?? this.namaUniversity,
      kodeUniversity: kodeUniversity ?? this.kodeUniversity,
      alamatUniversity: alamatUniversity ?? this.alamatUniversity,
      websiteUniversity: websiteUniversity ?? this.websiteUniversity,
      namaPemohon: namaPemohon ?? this.namaPemohon,
      email: email ?? this.email,
      nim: nim ?? this.nim,
      status: status ?? this.status,
      catatanAdmin: catatanAdmin ?? this.catatanAdmin,
      processedAt: processedAt ?? this.processedAt,
      processedBy: processedBy ?? this.processedBy,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  List<Object?> get props => [
        id,
        namaUniversity,
        kodeUniversity,
        alamatUniversity,
        websiteUniversity,
        namaPemohon,
        email,
        nim,
        status,
        catatanAdmin,
        processedAt,
        processedBy,
        createdAt,
        updatedAt,
      ];
}

// Request DTO for creating university request
class CreateUniversityRequest extends BaseModel {
  final String namaUniversity;
  final String kodeUniversity;
  final String alamatUniversity;
  final String? websiteUniversity;
  final String namaPemohon;
  final String email;
  final String nim;

  const CreateUniversityRequest({
    required this.namaUniversity,
    required this.kodeUniversity,
    required this.alamatUniversity,
    this.websiteUniversity,
    required this.namaPemohon,
    required this.email,
    required this.nim,
  });

  factory CreateUniversityRequest.fromJson(Map<String, dynamic> json) {
    return CreateUniversityRequest(
      namaUniversity: json['nama_university'] ?? '',
      kodeUniversity: json['kode_university'] ?? '',
      alamatUniversity: json['alamat_university'] ?? '',
      websiteUniversity: json['website_university'],
      namaPemohon: json['nama_pemohon'] ?? '',
      email: json['email'] ?? '',
      nim: json['nim'] ?? '',
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'nama_university': namaUniversity,
      'kode_university': kodeUniversity,
      'alamat_university': alamatUniversity,
      'website_university': websiteUniversity,
      'nama_pemohon': namaPemohon,
      'email': email,
      'nim': nim,
    };
  }

  @override
  List<Object?> get props => [
        namaUniversity,
        kodeUniversity,
        alamatUniversity,
        websiteUniversity,
        namaPemohon,
        email,
        nim,
      ];
}

// Universities with pagination response
class UniversitiesResponse extends BaseModel {
  final List<University> universities;
  final PaginationMeta pagination;

  const UniversitiesResponse({
    required this.universities,
    required this.pagination,
  });

  factory UniversitiesResponse.fromJson(Map<String, dynamic> json) {
    return UniversitiesResponse(
      universities: (json['universities'] as List? ?? [])
          .map((item) => University.fromJson(item as Map<String, dynamic>))
          .toList(),
      pagination: PaginationMeta.fromJson(json['pagination'] ?? {}),
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'universities': universities.map((u) => u.toJson()).toList(),
      'pagination': pagination.toJson(),
    };
  }

  @override
  List<Object?> get props => [universities, pagination];
}