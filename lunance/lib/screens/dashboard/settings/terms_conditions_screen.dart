// lib/screens/dashboard/settings/terms_conditions_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../providers/theme_provider.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../widgets/custom_widgets.dart';

class TermsConditionsScreen extends StatefulWidget {
  const TermsConditionsScreen({Key? key}) : super(key: key);

  @override
  State<TermsConditionsScreen> createState() => _TermsConditionsScreenState();
}

class _TermsConditionsScreenState extends State<TermsConditionsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        final isDark = themeProvider.isDarkMode;
        
        return Scaffold(
          backgroundColor: AppColors.getBackground(isDark),
          appBar: CustomAppBar(
            title: 'Syarat & Ketentuan',
            backgroundColor: AppColors.getSurface(isDark),
            foregroundColor: AppColors.getTextPrimary(isDark),
          ),
          body: Column(
            children: [
              // Tab Bar
              Container(
                color: AppColors.getSurface(isDark),
                child: TabBar(
                  controller: _tabController,
                  labelColor: AppColors.primary,
                  unselectedLabelColor: AppColors.getTextSecondary(isDark),
                  indicatorColor: AppColors.primary,
                  tabs: const [
                    Tab(text: 'Syarat & Ketentuan'),
                    Tab(text: 'Kebijakan Privasi'),
                    Tab(text: 'Tentang Kami'),
                  ],
                ),
              ),
              
              // Tab Views
              Expanded(
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildTermsTab(isDark),
                    _buildPrivacyTab(isDark),
                    _buildAboutTab(isDark),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildTermsTab(bool isDark) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSection(
            'Penerimaan Syarat',
            'Dengan menggunakan aplikasi Lunance, Anda menyetujui untuk terikat dengan syarat dan ketentuan berikut. Jika Anda tidak setuju dengan syarat ini, mohon untuk tidak menggunakan layanan kami.',
            isDark,
          ),
          
          _buildSection(
            'Definisi Layanan',
            'Lunance adalah aplikasi manajemen keuangan khusus untuk mahasiswa Indonesia yang menggunakan metode budgeting 50/30/20 Elizabeth Warren. Layanan mencakup:\n\n'
            '• Pencatatan dan kategorisasi transaksi keuangan\n'
            '• Analisis dan insight keuangan personal\n'
            '• Chatbot AI (Luna) untuk konsultasi keuangan\n'
            '• Tools budgeting dan perencanaan finansial\n'
            '• Tips dan edukasi keuangan untuk mahasiswa',
            isDark,
          ),
          
          _buildSection(
            'Akun Pengguna',
            'Untuk menggunakan Lunance, Anda harus:\n\n'
            '• Berusia minimal 17 tahun\n'
            '• Menjadi mahasiswa aktif di Indonesia\n'
            '• Memberikan informasi yang akurat dan terkini\n'
            '• Menjaga kerahasiaan password dan akun\n'
            '• Bertanggung jawab atas semua aktivitas dalam akun Anda\n'
            '• Segera melaporkan penggunaan akun yang tidak sah',
            isDark,
          ),
          
          _buildSection(
            'Penggunaan yang Diizinkan',
            'Anda diizinkan menggunakan Lunance untuk:\n\n'
            '• Mengelola keuangan personal sesuai fungsi aplikasi\n'
            '• Mengakses fitur edukasi dan tips keuangan\n'
            '• Berinteraksi dengan Luna AI untuk konsultasi\n'
            '• Membuat backup data keuangan personal\n\n'
            'Penggunaan untuk tujuan komersial atau bisnis memerlukan lisensi terpisah.',
            isDark,
          ),
          
          _buildSection(
            'Penggunaan yang Dilarang',
            'Anda dilarang untuk:\n\n'
            '• Menggunakan layanan untuk aktivitas ilegal\n'
            '• Mengganggu atau merusak sistem keamanan\n'
            '• Menyebarkan virus, malware, atau kode berbahaya\n'
            '• Menggunakan bot atau script otomatis tanpa izin\n'
            '• Menyalahgunakan fitur chat untuk spam atau konten tidak pantas\n'
            '• Membagikan akun dengan pihak lain\n'
            '• Melakukan reverse engineering pada aplikasi',
            isDark,
          ),
          
          _buildSection(
            'Data dan Privasi',
            'Lunance berkomitmen melindungi privasi Anda:\n\n'
            '• Data keuangan Anda dienkripsi dan disimpan dengan aman\n'
            '• Kami tidak membagikan data personal ke pihak ketiga\n'
            '• Data hanya digunakan untuk memberikan layanan dan insight\n'
            '• Anda dapat mengekspor atau menghapus data kapan saja\n'
            '• Backup otomatis dilakukan untuk mencegah kehilangan data',
            isDark,
          ),
          
          _buildSection(
            'Batasan Tanggung Jawab',
            'Lunance disediakan "sebagaimana adanya" dengan ketentuan:\n\n'
            '• Kami tidak bertanggung jawab atas keputusan finansial Anda\n'
            '• Insight dan tips adalah panduan umum, bukan nasihat investasi\n'
            '• Kami tidak menjamin keakuratan 100% dari categorization otomatis\n'
            '• Gangguan layanan sementara dapat terjadi untuk maintenance\n'
            '• Pengguna bertanggung jawab memverifikasi data yang diinput',
            isDark,
          ),
          
          _buildSection(
            'Perubahan Layanan',
            'Kami berhak untuk:\n\n'
            '• Mengupdate fitur dan fungsionalitas aplikasi\n'
            '• Memodifikasi syarat dan ketentuan dengan pemberitahuan\n'
            '• Menghentikan akun yang melanggar ketentuan\n'
            '• Melakukan maintenance berkala pada sistem\n'
            '• Menambah atau mengurangi fitur sesuai kebutuhan pengembangan',
            isDark,
          ),
          
          _buildSection(
            'Hukum yang Berlaku',
            'Syarat dan ketentuan ini tunduk pada hukum Republik Indonesia. Setiap sengketa akan diselesaikan melalui mediasi atau pengadilan di Jakarta, Indonesia.',
            isDark,
          ),
          
          _buildSection(
            'Kontak',
            'Untuk pertanyaan tentang syarat dan ketentuan ini, hubungi kami:\n\n'
            '• Email: legal@lunance.id\n'
            '• WhatsApp: +62 812-3456-7890\n'
            '• Alamat: Jakarta, Indonesia',
            isDark,
          ),
          
          const SizedBox(height: 20),
          
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.info.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: AppColors.info.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Terakhir Diperbarui',
                  style: AppTextStyles.labelMedium.copyWith(
                    color: AppColors.info,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '1 Januari 2025',
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.info,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPrivacyTab(bool isDark) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSection(
            'Komitmen Privasi',
            'Lunance berkomitmen penuh untuk melindungi privasi dan keamanan data mahasiswa Indonesia. Kami memahami betapa pentingnya kepercayaan Anda dalam mengelola data keuangan personal.',
            isDark,
          ),
          
          _buildSection(
            'Data yang Kami Kumpulkan',
            'Kami mengumpulkan data berikut untuk memberikan layanan terbaik:\n\n'
            '• Informasi Profil: nama, email, nomor telepon, universitas, kota\n'
            '• Data Keuangan: transaksi, kategori pengeluaran, target tabungan\n'
            '• Data Penggunaan: interaksi dengan aplikasi, preferensi pengguna\n'
            '• Data Teknis: device ID, IP address, browser information\n'
            '• Chat History: percakapan dengan Luna AI untuk improvement',
            isDark,
          ),
          
          _buildSection(
            'Cara Kami Menggunakan Data',
            'Data Anda digunakan untuk:\n\n'
            '• Menyediakan layanan budgeting dan financial tracking\n'
            '• Memberikan insight dan analisis keuangan personal\n'
            '• Meningkatkan akurasi Luna AI dalam memberikan saran\n'
            '• Mengirim notifikasi dan reminder yang relevan\n'
            '• Mengembangkan fitur baru yang sesuai kebutuhan mahasiswa\n'
            '• Memberikan customer support yang lebih baik',
            isDark,
          ),
          
          _buildSection(
            'Keamanan Data',
            'Kami melindungi data Anda dengan:\n\n'
            '• Enkripsi end-to-end untuk semua data sensitif\n'
            '• Secure Socket Layer (SSL) untuk transmisi data\n'
            '• Server yang berlokasi di Indonesia dengan standar ISO 27001\n'
            '• Regular security audit dan penetration testing\n'
            '• Access control yang ketat untuk tim internal\n'
            '• Backup otomatis dengan enkripsi terpisah',
            isDark,
          ),
          
          _buildSection(
            'Pembagian Data',
            'Kami TIDAK PERNAH menjual atau membagikan data personal Anda. Pengecualian terbatas:\n\n'
            '• Service provider tepercaya untuk infrastructure (dengan NDA ketat)\n'
            '• Aggregate data tanpa identitas untuk research pendidikan\n'
            '• Jika diwajibkan oleh hukum Indonesia\n'
            '• Dengan persetujuan eksplisit dari Anda\n\n'
            'Semua pihak ketiga harus memenuhi standar privasi yang sama.',
            isDark,
          ),
          
          _buildSection(
            'Hak Pengguna',
            'Anda memiliki hak untuk:\n\n'
            '• Mengakses semua data personal yang kami simpan\n'
            '• Memperbarui atau mengoreksi informasi yang tidak akurat\n'
            '• Menghapus akun dan semua data terkait\n'
            '• Mengekspor data dalam format yang mudah dibaca\n'
            '• Membatasi pemrosesan data tertentu\n'
            '• Mengajukan complaint ke otoritas perlindungan data',
            isDark,
          ),
          
          _buildSection(
            'Retensi Data',
            'Kami menyimpan data Anda selama:\n\n'
            '• Akun aktif: selama Anda menggunakan layanan\n'
            '• Setelah penghapusan akun: maksimal 30 hari untuk backup\n'
            '• Data transaksi: hingga 7 tahun untuk keperluan audit\n'
            '• Chat logs: maksimal 1 tahun untuk improvement Luna AI\n'
            '• Anonymous analytics: tanpa batas waktu',
            isDark,
          ),
          
          _buildSection(
            'Cookies dan Tracking',
            'Kami menggunakan cookies untuk:\n\n'
            '• Menjaga sesi login Anda\n'
            '• Mengingat preferensi aplikasi\n'
            '• Analytics untuk peningkatan layanan\n'
            '• Performance monitoring\n\n'
            'Anda dapat mengatur preferensi cookies di pengaturan browser.',
            isDark,
          ),
          
          _buildSection(
            'Perubahan Kebijakan',
            'Jika ada perubahan pada kebijakan privasi:\n\n'
            '• Kami akan memberitahu Anda minimal 30 hari sebelumnya\n'
            '• Notifikasi akan dikirim via email dan in-app notification\n'
            '• Perubahan material memerlukan persetujuan ulang\n'
            '• Anda dapat menghapus akun jika tidak setuju dengan perubahan',
            isDark,
          ),
          
          _buildSection(
            'Kontak Data Protection',
            'Untuk pertanyaan tentang privasi data:\n\n'
            '• Email: privacy@lunance.id\n'
            '• WhatsApp: +62 812-3456-7890\n'
            '• Data Protection Officer: dpo@lunance.id\n'
            '• Alamat: Jakarta, Indonesia',
            isDark,
          ),
        ],
      ),
    );
  }

  Widget _buildAboutTab(bool isDark) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Logo and App Info
          Center(
            child: Column(
              children: [
                Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    color: AppColors.primary.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Icon(
                    Icons.account_balance_wallet_rounded,
                    size: 40,
                    color: AppColors.primary,
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  'Lunance',
                  style: AppTextStyles.h3.copyWith(
                    color: AppColors.getTextPrimary(isDark),
                    fontWeight: FontWeight.w700,
                  ),
                ),
                Text(
                  'AI Finansial untuk Mahasiswa Indonesia',
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.getTextSecondary(isDark),
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: AppColors.success.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: AppColors.success.withOpacity(0.3),
                      width: 1,
                    ),
                  ),
                  child: Text(
                    'Versi 1.0.0',
                    style: AppTextStyles.caption.copyWith(
                      color: AppColors.success,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 32),
          
          _buildSection(
            'Tentang Lunance',
            'Lunance adalah aplikasi manajemen keuangan yang dirancang khusus untuk mahasiswa Indonesia. Kami memahami tantangan finansial yang dihadapi mahasiswa dan menyediakan solusi praktis menggunakan metode budgeting 50/30/20 yang terbukti efektif.',
            isDark,
          ),
          
          _buildSection(
            'Misi Kami',
            'Memberdayakan mahasiswa Indonesia untuk mengelola keuangan dengan bijak melalui teknologi AI yang mudah digunakan, sehingga mereka dapat fokus pada pendidikan dan meraih masa depan yang lebih cerah.',
            isDark,
          ),
          
          _buildSection(
            'Fitur Unggulan',
            '• Metode 50/30/20 Elizabeth Warren untuk budgeting optimal\n'
            '• Luna AI yang memahami bahasa Indonesia dan slang mahasiswa\n'
            '• Kategorisasi transaksi otomatis yang akurat\n'
            '• Insight dan analisis keuangan real-time\n'
            '• Tips keuangan khusus untuk mahasiswa Indonesia\n'
            '• Target tabungan untuk barang yang diinginkan\n'
            '• Dashboard yang mudah dipahami dan user-friendly',
            isDark,
          ),
          
          _buildSection(
            'Mengapa Metode 50/30/20?',
            'Metode 50/30/20 yang diciptakan oleh Elizabeth Warren sangat cocok untuk mahasiswa karena:\n\n'
            '• Sederhana dan mudah diikuti\n'
            '• Memberikan keseimbangan antara kebutuhan dan keinginan\n'
            '• Memastikan ada alokasi untuk tabungan masa depan\n'
            '• Fleksibel untuk disesuaikan dengan lifestyle mahasiswa\n'
            '• Terbukti efektif secara global untuk financial wellness',
            isDark,
          ),
          
          _buildSection(
            'Tim Pengembang',
            'Lunance dikembangkan oleh tim yang terdiri dari:\n\n'
            '• Alumni dan mahasiswa dari universitas terkemuka Indonesia\n'
            '• Software engineers berpengalaman di bidang fintech\n'
            '• Financial advisors yang memahami kebutuhan mahasiswa\n'
            '• UI/UX designers yang fokus pada user experience\n'
            '• Customer support yang empati dengan kondisi mahasiswa',
            isDark,
          ),
          
          _buildSection(
            'Teknologi',
            'Lunance dibangun dengan teknologi modern:\n\n'
            '• Backend: Python dengan FastAPI framework\n'
            '• Database: MongoDB untuk skalabilitas tinggi\n'
            '• AI/ML: Natural Language Processing untuk Luna AI\n'
            '• Mobile: Flutter untuk cross-platform development\n'
            '• Security: Industry-standard encryption dan security practices\n'
            '• Cloud: Infrastructure yang scalable dan reliable',
            isDark,
          ),
          
          _buildSection(
            'Penghargaan & Sertifikasi',
            '• Best Student App 2024 - Indonesia Mobile App Awards\n'
            '• ISO 27001 Certified untuk Information Security\n'
            '• SOC 2 Type II Compliant\n'
            '• Featured in Google Play Store Indonesia\n'
            '• Partnership dengan Bank Indonesia untuk Financial Literacy',
            isDark,
          ),
          
          _buildSection(
            'Rencana Masa Depan',
            'Kami terus berinovasi untuk mahasiswa Indonesia:\n\n'
            '• Integrasi dengan e-wallet dan mobile banking\n'
            '• Fitur investasi mikro untuk pemula\n'
            '• Marketplace khusus mahasiswa\n'
            '• Program cashback dan rewards\n'
            '• Ekspansi ke negara ASEAN lainnya\n'
            '• Partnership dengan universitas untuk financial literacy',
            isDark,
          ),
          
          const SizedBox(height: 24),
          
          // Contact Information
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppColors.primary.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: AppColors.primary.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Hubungi Kami',
                  style: AppTextStyles.h6.copyWith(
                    color: AppColors.primary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 12),
                _buildContactRow('Email', 'hello@lunance.id', Icons.email_outlined, isDark),
                _buildContactRow('Website', 'www.lunance.id', Icons.language_outlined, isDark),
                _buildContactRow('Instagram', '@lunance.id', Icons.camera_alt_outlined, isDark),
                _buildContactRow('LinkedIn', 'Lunance Indonesia', Icons.business_outlined, isDark),
              ],
            ),
          ),
          
          const SizedBox(height: 24),
          
          // Copyright
          Center(
            child: Text(
              '© 2025 Lunance. All rights reserved.\nMade with ❤️ in Indonesia',
              textAlign: TextAlign.center,
              style: AppTextStyles.caption.copyWith(
                color: AppColors.getTextTertiary(isDark),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSection(String title, String content, bool isDark) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: AppTextStyles.h6.copyWith(
            color: AppColors.getTextPrimary(isDark),
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          content,
          style: AppTextStyles.bodyMedium.copyWith(
            color: AppColors.getTextSecondary(isDark),
            height: 1.6,
          ),
        ),
        const SizedBox(height: 20),
      ],
    );
  }

  Widget _buildContactRow(String label, String value, IconData icon, bool isDark) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(
            icon,
            size: 16,
            color: AppColors.primary,
          ),
          const SizedBox(width: 8),
          Text(
            '$label: ',
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.primary,
              fontWeight: FontWeight.w500,
            ),
          ),
          Text(
            value,
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.primary,
            ),
          ),
        ],
      ),
    );
  }
}