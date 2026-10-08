export type Language = "en" | "id";

export const translations = {
  en: {
    navbar: {
      home: "Home",
      detection: "Detection",
      history: "History",
      education: "Education",
      language: "English"
    },

    footer: {
      description:
        "An AI-powered web application for detecting unauthorized digital transactions using a Hybrid XGBoost + LSTM model.",
      copyright: "© 2026 FraudDetect. All rights reserved."
    },

    home: {
      badge: "AI-Powered Transaction Security",

      title: "Detect Unauthorized Digital Transactions",

      highlight: " Faster & Smarter",

      description:
        "A web-based intelligent system that detects unauthorized digital payment transactions using a Hybrid XGBoost + LSTM model for accurate, reliable, and real-time prediction.",

      start: "Start Detection",

      learn: "Learn More",

      stats: {
        transactions: "Transactions",
        accuracy: "Accuracy",
        precision: "Precision",
        recall: "Recall"
      },

      workflow: {
        title: "How It Works",

        step1: "Transaction Input",
        step1Desc: "Enter transaction information.",

        step2: "Data Processing",
        step2Desc: "Transaction features are prepared for AI analysis.",

        step3: "AI Prediction",
        step3Desc: "Hybrid XGBoost + LSTM analyzes the transaction.",

        step4: "Security Decision",
        step4Desc: "Receive prediction results and recommendations."
      },

      technology: {
        title: "Hybrid AI Model",

        xgb: "Tree-based machine learning for structured transaction data.",

        lstm: "Deep learning for sequential transaction behavior."
      },

      cta: {
        title: "Ready to Analyze Your Transactions?",

        description:
          "Start using our AI-powered transaction security system today.",

        button: "Get Started"
      }
    },
    detection: {
      title: "Transaction Detection",

      description:
        "Enter transaction information below to analyze whether a transaction is legitimate or unauthorized using our Hybrid AI model.",

      form: {
        title: "Transaction Information",

        amount: "Transaction Amount",
        amountPlaceholder: "Enter amount",

        product: "Product Code",
        productPlaceholder: "Select Product",

        card: "Card Type",
        cardPlaceholder: "Select Card",

        email: "Email Domain",
        emailPlaceholder: "gmail.com",

        time: "Transaction Time",

        button: "Analyze Transaction"
      },

      result: {
        title: "Detection Result",

        status: "Status",

        legitimate: "Legitimate",

        unauthorized: "Unauthorized",

        probability: "Unauthorized Probability",

        recommendation: "Security Recommendation",

        safeMessage:
          "This transaction appears legitimate and may proceed normally.",

        fraudMessage:
          "This transaction is considered suspicious. Additional verification is recommended.",

        ClearResults:
          "Clear Results",

        SaveToHistory:
          "Save To History",
        emptyMessage: "Enter transaction information and click Analyze Transaction to see the detection result."
      },
      modes: { single: "Single Transaction", upload: "Upload Transaction File" },
      recommendations: {
        low: "This transaction appears legitimate. No significant unauthorized activity was detected.",
        medium: "This transaction shows some suspicious characteristics. Additional verification is recommended.",
        high: "This transaction shows a high risk of unauthorized activity. Please verify the transaction before proceeding.",
        critical: "This transaction is highly suspicious. Additional verification is strongly recommended before proceeding."
      },
      messages: { completeFields: "Please complete all transaction fields.", csvOnly: "Please upload a CSV file.", singleError: "Failed to analyze transaction.", csvError: "Failed to analyze CSV file." },
      actions: { analyzing: "Analyzing...", analyzingTransactions: "Analyzing Transactions...", analyzeTransactions: "Analyze Transactions" },
      upload: {
        title: "Upload Transaction File", description: "Upload a CSV file containing transaction data for multiple transaction detection.",
        templateTitle: "CSV Template", templateDescription: "Not sure about the required CSV structure? Download our sample template first.", downloadSample: "Download CSV Sample",
        dropTitle: "Drop your CSV file here", dropDescription: "or click to browse from your computer", supportedFormat: "Supported format: CSV", remove: "Remove",
        previewTitle: "CSV Preview", previewDescription: (count: number) => "Showing the first " + count + " rows",
        completedEyebrow: "ANALYSIS COMPLETED", analysisResult: "Analysis Result", completedDescription: "The uploaded transaction file has been successfully analyzed.", completed: "Completed",
        totalTransactions: "Total Transactions", fraudDetected: "Fraud Detected", safeTransactions: "Safe Transactions", detectionOverview: "Detection Overview", fraudRate: "% fraud rate", fraud: "Fraud", safe: "Safe",
        predictionDetails: "Prediction Details", predictionDescription: "Showing prediction results from the analyzed transactions.", row: "Row", fraudScore: "Fraud Score"
      },
      status: { fraud: "FRAUD DETECTED", safe: "SAFE" }
    },

    history: {
      title: "Detection History",

      description:
        "Review previous transaction detection results generated by the Hybrid AI system.",

      search: "Search transaction...",

      filter: {
        all: "All Status",
        legitimate: "Legitimate",
        unauthorized: "Unauthorized"
      },

      amount: "Amount",

      probability: "Probability",

      date: "Date"
    },

    education: {
      title: "Fraud Detection Education",

      description:
        "Learn about unauthorized transactions, artificial intelligence, and how the Hybrid XGBoost + LSTM model improves transaction security.",

      unauthorized: {
        title: "What is an Unauthorized Transaction?",

        content:
          "An unauthorized transaction is any payment or financial activity performed without the account owner's permission. Such transactions may occur because of stolen payment cards, phishing attacks, account takeovers, or identity theft."
      },

      types: {
        title: "Common Types of Unauthorized Transactions",

        card: "Card Fraud",

        cardDesc: "Unauthorized use of debit or credit card information.",

        identity: "Identity Theft",

        identityDesc:
          "Using another person's identity to perform financial transactions.",

        account: "Account Takeover",

        accountDesc: "Attackers gain access to a user's payment account.",

        phishing: "Phishing",

        phishingDesc:
          "Fake emails or websites designed to steal sensitive information."
      },

      workflow: {
        title: "How Our AI Works",
        transaction: "Transaction",
        preprocessing: "Preprocessing",
        featureEngineering: "Feature Engineering",
        xgboost: "XGBoost",
        lstm: "LSTM",
        prediction: "Prediction"
      },

      advantages: {
        title: "Why Hybrid XGBoost + LSTM?",

        accuracy: "High Accuracy",

        accuracyDesc: "Combines tree-based machine learning and deep learning.",

        realtime: "Real-Time Prediction",

        realtimeDesc: "Fast enough for modern digital payment systems.",

        pattern: "Pattern Recognition",

        patternDesc: "Automatically detects complex transaction behaviors."
      },

      faq: {
        title: "Frequently Asked Questions",

        q1: "What does the AI predict?",

        a1: "The AI predicts whether a transaction is likely to be legitimate or unauthorized.",

        q2: "Can this replace manual verification?",

        a2: "No. The system is designed as a decision-support tool to help identify suspicious transactions."
      }
    }
  },

  id: {
    navbar: {
      home: "Beranda",
      detection: "Deteksi",
      history: "Riwayat",
      education: "Edukasi",
      language: "Indonesia"
    },

    footer: {
      description:
        "Aplikasi berbasis AI untuk mendeteksi transaksi digital tidak sah menggunakan model Hybrid XGBoost + LSTM.",

      copyright: "© 2026 FraudDetect. Seluruh hak cipta dilindungi."
    },

    home: {
      badge: "Keamanan Transaksi Berbasis AI",

      title: "Deteksi Transaksi Digital Tidak Sah",

      highlight: " Lebih Cepat & Cerdas",

      description:
        "Sistem cerdas berbasis web yang mendeteksi transaksi pembayaran digital tidak sah menggunakan model Hybrid XGBoost + LSTM secara akurat, andal, dan real-time.",

      start: "Mulai Deteksi",

      learn: "Pelajari Selengkapnya",

      stats: {
        transactions: "Transaksi",
        accuracy: "Akurasi",
        precision: "Presisi",
        recall: "Recall"
      },

      workflow: {
        title: "Cara Kerja",

        step1: "Input Transaksi",
        step1Desc: "Masukkan informasi transaksi.",

        step2: "Pemrosesan Data",
        step2Desc: "Fitur transaksi dipersiapkan untuk analisis AI.",

        step3: "Prediksi AI",
        step3Desc: "Model Hybrid XGBoost + LSTM menganalisis transaksi.",

        step4: "Keputusan Keamanan",
        step4Desc: "Sistem memberikan hasil prediksi dan rekomendasi."
      },

      technology: {
        title: "Model AI Hybrid",

        xgb: "Machine learning berbasis pohon keputusan untuk data transaksi terstruktur.",

        lstm: "Deep learning untuk mempelajari pola transaksi secara berurutan."
      },

      cta: {
        title: "Siap Menganalisis Transaksi Anda?",

        description:
          "Mulai gunakan sistem keamanan transaksi berbasis AI sekarang.",

        button: "Mulai"
      }
    },
    detection: {
      title: "Deteksi Transaksi",

      description:
        "Masukkan informasi transaksi di bawah ini untuk menganalisis apakah transaksi tergolong sah atau tidak sah menggunakan model AI Hybrid.",

      form: {
        title: "Informasi Transaksi",

        amount: "Jumlah Transaksi",
        amountPlaceholder: "Masukkan nominal",

        product: "Kode Produk",
        productPlaceholder: "Pilih Produk",

        card: "Jenis Kartu",
        cardPlaceholder: "Pilih Kartu",

        email: "Domain Email",
        emailPlaceholder: "gmail.com",

        time: "Waktu Transaksi",

        button: "Analisis Transaksi"
      },

      result: {
        title: "Hasil Deteksi",

        status: "Status",

        legitimate: "Sah",

        unauthorized: "Tidak Sah",

        probability: "Probabilitas Transaksi Tidak Sah",

        recommendation: "Rekomendasi Keamanan",

        safeMessage:
          "Transaksi ini terindikasi sah dan dapat diproses seperti biasa.",

        fraudMessage:
          "Transaksi ini terindikasi mencurigakan. Disarankan melakukan verifikasi tambahan.",

        ClearResults:
          "Hapus Hasil",

        SaveToHistory:
          "Simpan ke Riwayat",
        emptyMessage: "Masukkan informasi transaksi lalu klik Analisis Transaksi untuk melihat hasil deteksi."
      },
      modes: { single: "Transaksi Tunggal", upload: "Unggah File Transaksi" },
      recommendations: {
        low: "Transaksi ini terindikasi sah. Tidak ditemukan aktivitas tidak sah yang signifikan.",
        medium: "Transaksi ini menunjukkan beberapa karakteristik mencurigakan. Disarankan melakukan verifikasi tambahan.",
        high: "Transaksi ini menunjukkan risiko tinggi aktivitas tidak sah. Silakan verifikasi transaksi sebelum melanjutkan.",
        critical: "Transaksi ini sangat mencurigakan. Sangat disarankan melakukan verifikasi tambahan sebelum melanjutkan."
      },
      messages: { completeFields: "Harap lengkapi semua data transaksi.", csvOnly: "Silakan unggah file CSV.", singleError: "Gagal menganalisis transaksi.", csvError: "Gagal menganalisis file CSV." },
      actions: { analyzing: "Menganalisis...", analyzingTransactions: "Menganalisis Transaksi...", analyzeTransactions: "Analisis Transaksi" },
      upload: {
        title: "Unggah File Transaksi", description: "Unggah file CSV yang berisi data transaksi untuk mendeteksi beberapa transaksi.",
        templateTitle: "Template CSV", templateDescription: "Tidak yakin dengan struktur CSV yang diperlukan? Unduh template contoh terlebih dahulu.", downloadSample: "Unduh Contoh CSV",
        dropTitle: "Letakkan file CSV di sini", dropDescription: "atau klik untuk memilih dari komputer", supportedFormat: "Format yang didukung: CSV", remove: "Hapus",
        previewTitle: "Pratinjau CSV", previewDescription: (count: number) => "Menampilkan " + count + " baris pertama",
        completedEyebrow: "ANALISIS SELESAI", analysisResult: "Hasil Analisis", completedDescription: "File transaksi yang diunggah telah berhasil dianalisis.", completed: "Selesai",
        totalTransactions: "Total Transaksi", fraudDetected: "Fraud Terdeteksi", safeTransactions: "Transaksi Aman", detectionOverview: "Ringkasan Deteksi", fraudRate: "% tingkat fraud", fraud: "Fraud", safe: "Aman",
        predictionDetails: "Detail Prediksi", predictionDescription: "Menampilkan hasil prediksi dari transaksi yang telah dianalisis.", row: "Baris", fraudScore: "Skor Fraud"
      },
      status: { fraud: "FRAUD TERDETEKSI", safe: "AMAN" }
    },

    history: {
      title: "Riwayat Deteksi",

      description:
        "Tinjau kembali hasil deteksi transaksi yang telah diproses oleh sistem AI Hybrid.",

      search: "Cari transaksi...",

      filter: {
        all: "Semua Status",
        legitimate: "Sah",
        unauthorized: "Tidak Sah"
      },

      amount: "Jumlah",

      probability: "Probabilitas",

      date: "Tanggal"
    },

    education: {
      title: "Edukasi Deteksi Transaksi",

      description:
        "Pelajari tentang transaksi tidak sah, kecerdasan buatan, dan bagaimana model Hybrid XGBoost + LSTM meningkatkan keamanan transaksi digital.",

      unauthorized: {
        title: "Apa itu Transaksi Tidak Sah?",

        content:
          "Transaksi tidak sah adalah aktivitas pembayaran atau keuangan yang dilakukan tanpa izin dari pemilik akun. Hal ini dapat terjadi akibat pencurian kartu, serangan phishing, pengambilalihan akun, atau pencurian identitas."
      },

      types: {
        title: "Jenis Umum Transaksi Tidak Sah",

        card: "Penyalahgunaan Kartu",

        cardDesc:
          "Penggunaan informasi kartu debit atau kartu kredit tanpa izin.",

        identity: "Pencurian Identitas",

        identityDesc:
          "Menggunakan identitas orang lain untuk melakukan transaksi.",

        account: "Pengambilalihan Akun",

        accountDesc:
          "Penyerang berhasil memperoleh akses ke akun pembayaran pengguna.",

        phishing: "Phishing",

        phishingDesc:
          "Email atau situs web palsu yang bertujuan mencuri informasi penting pengguna."
      },

      workflow: {
        title: "Cara Kerja AI Kami",
        transaction: "Transaksi",
        preprocessing: "Pra-pemrosesan",
        featureEngineering: "Rekayasa Fitur",
        xgboost: "XGBoost",
        lstm: "LSTM",
        prediction: "Prediksi"
      },

      advantages: {
        title: "Mengapa Hybrid XGBoost + LSTM?",

        accuracy: "Akurasi Tinggi",

        accuracyDesc:
          "Menggabungkan machine learning berbasis pohon keputusan dan deep learning.",

        realtime: "Prediksi Real-Time",

        realtimeDesc:
          "Cukup cepat untuk mendukung sistem pembayaran digital modern.",

        pattern: "Pengenalan Pola",

        patternDesc: "Mendeteksi pola transaksi yang kompleks secara otomatis."
      },

      faq: {
        title: "Pertanyaan yang Sering Diajukan",

        q1: "Apa yang diprediksi oleh AI?",

        a1: "AI memprediksi apakah suatu transaksi kemungkinan besar tergolong sah atau tidak sah.",

        q2: "Apakah sistem ini dapat menggantikan verifikasi manual?",

        a2: "Tidak. Sistem ini dirancang sebagai alat bantu pengambilan keputusan untuk membantu mengidentifikasi transaksi yang mencurigakan."
      }
    }
  }
};
