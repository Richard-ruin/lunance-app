// lib/screens/dashboard/settings/help_support_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../providers/theme_provider.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../widgets/custom_widgets.dart';

class HelpSupportScreen extends StatefulWidget {
  const HelpSupportScreen({Key? key}) : super(key: key);

  @override
  State<HelpSupportScreen> createState() => _HelpSupportScreenState();
}

class _HelpSupportScreenState extends State<HelpSupportScreen> {
  final List<FAQItem> _faqItems = [
    FAQItem(
      question: 'Apa itu metode 50/30/20?',
      answer: 'Metode 50/30/20 adalah strategi budgeting yang membagi pemasukan menjadi tiga kategori:\n\n'
          '• 50% untuk NEEDS (Kebutuhan): kos, makan, transport, pendidikan\n'
          '• 30% untuk WANTS (Keinginan): hiburan, jajan, shopping, target tabungan barang\n'
          '• 20% untuk SAVINGS (Tabungan): dana darurat, investasi, modal usaha\n\n'
          'Metode ini diciptakan oleh Elizabeth Warren dan sangat cocok untuk mahasiswa.',
    ),
    FAQItem(
      question: 'Bagaimana cara Luna AI membantu mengatur keuangan?',
      answer: 'Luna AI dapat membantu Anda dengan:\n\n'
          '• Mencatat transaksi otomatis melalui chat\n'
          '• Mengkategorikan pengeluaran sesuai metode 50/30/20\n'
          '• Memberikan insight dan analisis keuangan\n'
          '• Mengingatkan jika budget hampir habis\n'
          '• Memberikan tips keuangan khusus mahasiswa\n'
          '• Membantu membuat target tabungan untuk barang yang diinginkan',
    ),
    FAQItem(
      question: 'Apakah data keuangan saya aman?',
      answer: 'Ya, keamanan data Anda adalah prioritas utama kami:\n\n'
          '• Semua data dienkripsi dengan standar bank\n'
          '• Kami tidak menyimpan informasi rekening bank\n'
          '• Data hanya digunakan untuk memberikan insight personal\n'
          '• Tidak ada data yang dibagikan ke pihak ketiga\n'
          '• Anda dapat menghapus akun dan data kapan saja',
    ),
    FAQItem(
      question: 'Bagaimana cara mengubah budget allocation?',
      answer: 'Budget allocation dihitung otomatis berdasarkan pemasukan bulanan Anda:\n\n'
          '• Buka menu Pengaturan → Pengaturan Keuangan\n'
          '• Update pemasukan bulanan Anda\n'
          '• Budget 50/30/20 akan otomatis direcalculate\n'
          '• Anda bisa reset budget bulanan kapan saja\n\n'
          'Metode 50/30/20 sudah optimal untuk mahasiswa, namun Anda bisa menyesuaikan sesuai kebutuhan.',
    ),
    FAQItem(
      question: 'Apa yang dimaksud dengan kategori NEEDS, WANTS, dan SAVINGS?',
      answer: 'Kategori dalam metode 50/30/20:\n\n'
          'NEEDS (50%) - Kebutuhan pokok yang wajib:\n'
          '• Kos/tempat tinggal, makanan pokok, transportasi wajib\n'
          '• Pendidikan (buku, UKT, praktikum)\n'
          '• Internet & komunikasi, kesehatan & kebersihan\n\n'
          'WANTS (30%) - Keinginan yang bisa dikontrol:\n'
          '• Hiburan & sosial, jajan & snack, pakaian\n'
          '• Organisasi & event, target tabungan barang\n\n'
          'SAVINGS (20%) - Tabungan masa depan:\n'
          '• Dana darurat, investasi, modal usaha',
    ),
    FAQItem(
      question: 'Bagaimana cara chat dengan Luna AI?',
      answer: 'Luna AI sangat mudah digunakan:\n\n'
          '• Ketik transaksi dalam bahasa natural: "Beli nasi padang 15rb"\n'
          '• Luna akan otomatis kategorikan sesuai metode 50/30/20\n'
          '• Tanya insight: "Gimana pengeluaran bulan ini?"\n'
          '• Minta tips: "Tips hemat untuk mahasiswa dong"\n'
          '• Set target: "Mau nabung laptop 10 juta"\n\n'
          'Luna memahami bahasa Indonesia dan slang mahasiswa!',
    ),
    FAQItem(
      question: 'Apakah Lunance gratis?',
      answer: 'Ya, Lunance gratis untuk mahasiswa Indonesia:\n\n'
          '• Fitur budgeting 50/30/20 gratis selamanya\n'
          '• Chat dengan Luna AI unlimited\n'
          '• Analytics dan insights dasar gratis\n'
          '• Tracking transaksi tanpa batas\n\n'
          'Kami berkomitmen membantu mahasiswa Indonesia mengelola keuangan dengan baik.',
    ),
    FAQItem(
      question: 'Bagaimana cara menghubungi customer support?',
      answer: 'Kami siap membantu Anda 24/7:\n\n'
          '• Email: support@lunance.id\n'
          '• WhatsApp: +62 812-3456-7890\n'
          '• Instagram: @lunance.id\n'
          '• Live chat melalui aplikasi\n\n'
          'Tim support kami terdiri dari mahasiswa yang memahami kebutuhan finansial mahasiswa Indonesia.',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        final isDark = themeProvider.isDarkMode;
        
        return Scaffold(
          backgroundColor: AppColors.getBackground(isDark),
          appBar: CustomAppBar(
            title: 'Bantuan & Dukungan',
            backgroundColor: AppColors.getSurface(isDark),
            foregroundColor: AppColors.getTextPrimary(isDark),
          ),
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header Card
                _buildHeaderCard(isDark),
                
                const SizedBox(height: 24),
                
                // Quick Actions
                _buildQuickActions(isDark),
                
                const SizedBox(height: 24),
                
                // FAQ Section
                _buildFAQSection(isDark),
                
                const SizedBox(height: 24),
                
                // Contact Support
                _buildContactSupport(isDark),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildHeaderCard(bool isDark) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [AppColors.primary, AppColors.primaryDark],
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppColors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  Icons.support_agent_outlined,
                  color: AppColors.white,
                  size: 24,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Bantuan Lunance',
                      style: AppTextStyles.h6.copyWith(
                        color: AppColors.white,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      'Kami siap membantu Anda 24/7',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.white.withOpacity(0.9),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            'Tim support Lunance terdiri dari mahasiswa yang memahami kebutuhan finansial mahasiswa Indonesia. Jangan ragu untuk menghubungi kami!',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.white.withOpacity(0.9),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions(bool isDark) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Bantuan Cepat',
          style: AppTextStyles.h6.copyWith(
            color: AppColors.getTextPrimary(isDark),
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _buildQuickActionCard(
                'Live Chat',
                'Chat langsung dengan support',
                Icons.chat_outlined,
                AppColors.success,
                () => _openLiveChat(),
                isDark,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildQuickActionCard(
                'WhatsApp',
                'Hubungi via WhatsApp',
                Icons.phone_outlined,
                AppColors.info,
                () => _openWhatsApp(),
                isDark,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildQuickActionCard(
    String title,
    String subtitle,
    IconData icon,
    Color color,
    VoidCallback onTap,
    bool isDark,
  ) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isDark ? AppColors.gray800 : AppColors.gray50,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.getBorder(isDark)),
        ),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                icon,
                color: color,
                size: 24,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              title,
              style: AppTextStyles.labelMedium.copyWith(
                color: AppColors.getTextPrimary(isDark),
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: AppTextStyles.caption.copyWith(
                color: AppColors.getTextSecondary(isDark),
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFAQSection(bool isDark) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Frequently Asked Questions',
          style: AppTextStyles.h6.copyWith(
            color: AppColors.getTextPrimary(isDark),
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 12),
        ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: _faqItems.length,
          separatorBuilder: (context, index) => const SizedBox(height: 8),
          itemBuilder: (context, index) {
            return _buildFAQItem(_faqItems[index], isDark);
          },
        ),
      ],
    );
  }

  Widget _buildFAQItem(FAQItem item, bool isDark) {
    return Container(
      decoration: BoxDecoration(
        color: isDark ? AppColors.gray800 : AppColors.gray50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.getBorder(isDark)),
      ),
      child: ExpansionTile(
        title: Text(
          item.question,
          style: AppTextStyles.bodyMedium.copyWith(
            color: AppColors.getTextPrimary(isDark),
            fontWeight: FontWeight.w500,
          ),
        ),
        iconColor: AppColors.primary,
        collapsedIconColor: AppColors.getTextSecondary(isDark),
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            child: Text(
              item.answer,
              style: AppTextStyles.bodyMedium.copyWith(
                color: AppColors.getTextSecondary(isDark),
                height: 1.6,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildContactSupport(bool isDark) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: isDark ? AppColors.gray800 : AppColors.gray50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.getBorder(isDark)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Masih Butuh Bantuan?',
            style: AppTextStyles.h6.copyWith(
              color: AppColors.getTextPrimary(isDark),
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Tim support kami siap membantu Anda dengan pertanyaan apapun tentang Lunance.',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.getTextSecondary(isDark),
            ),
          ),
          const SizedBox(height: 16),
          
          _buildContactItem(
            'Email',
            'support@lunance.id',
            Icons.email_outlined,
            () => _sendEmail(),
            isDark,
          ),
          
          const SizedBox(height: 12),
          
          _buildContactItem(
            'WhatsApp',
            '+62 812-3456-7890',
            Icons.phone_outlined,
            () => _openWhatsApp(),
            isDark,
          ),
          
          const SizedBox(height: 12),
          
          _buildContactItem(
            'Instagram',
            '@lunance.id',
            Icons.camera_alt_outlined,
            () => _openInstagram(),
            isDark,
          ),
        ],
      ),
    );
  }

  Widget _buildContactItem(
    String label,
    String value,
    IconData icon,
    VoidCallback onTap,
    bool isDark,
  ) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Row(
          children: [
            Icon(
              icon,
              size: 20,
              color: AppColors.primary,
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.getTextSecondary(isDark),
                  ),
                ),
                Text(
                  value,
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.primary,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
            const Spacer(),
            Icon(
              Icons.arrow_forward_ios,
              size: 16,
              color: AppColors.getTextTertiary(isDark),
            ),
          ],
        ),
      ),
    );
  }

  void _openLiveChat() {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Fitur live chat akan segera tersedia'),
        backgroundColor: AppColors.info,
      ),
    );
  }

  void _openWhatsApp() {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Membuka WhatsApp...'),
        backgroundColor: AppColors.success,
      ),
    );
  }

  void _sendEmail() {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Membuka aplikasi email...'),
        backgroundColor: AppColors.info,
      ),
    );
  }

  void _openInstagram() {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Membuka Instagram...'),
        backgroundColor: AppColors.info,
      ),
    );
  }
}

class FAQItem {
  final String question;
  final String answer;

  FAQItem({
    required this.question,
    required this.answer,
  });
}