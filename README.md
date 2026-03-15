
# detector document by Vina

Plagiarism Detection Tool - Mendeteksi tingkat kemiripan antar dokumen teks dengan algoritma TF-IDF dan Cosine Similarity.

## Fitur Utama

- Deteksi kemiripan antar file teks (txt, pdf, docx)
- Batch processing (multiple files sekaligus)
- Similarity matrix visualization
- Cluster analysis untuk grup dokumen mirip
- Online source checking (Google search)
- JSON report generation
- Mode folder (scan semua file dalam folder)

## Cara Install

### Method 1: Install Langsung (Rekomendasi)

```bash
git clone https://github.com/VinJagocoding/detector-.git
cd detector-
pip install -r requirements.txt
```

Method 2: Install Manual (Jika Method 1 Gagal)

```bash
git clone https://github.com/VinJagocoding/detector-.git
cd detector-
pip install numpy
pip install pandas
pip install scikit-learn
pip install PyPDF2
pip install python-docx
pip install beautifulsoup4
pip install requests
```

Method 3: Untuk Termux (Android)

```bash
pkg update && pkg upgrade
pkg install python clang libxml2 libxslt binutils
git clone https://github.com/VinJagocoding/detector-.git
cd detector-
pip install -r requirements.txt
```

Jika error pandas:

```bash
pkg install binutils
pip install pandas --no-cache-dir
```

Method 4: Untuk Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3 python3-pip git
git clone https://github.com/VinJagocoding/detector-.git
cd detector-
pip3 install -r requirements.txt
```

Method 5: Untuk Windows (CMD/PowerShell)

```bash
git clone https://github.com/VinJagocoding/detector-.git
cd detector-
pip install -r requirements.txt
```

Jika error permission:

```bash
pip install --user -r requirements.txt
```

Method 6: Untuk macOS

```bash
# Install Homebrew dulu (jika belum)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python

# Clone dan install
git clone https://github.com/VinJagocoding/detector-.git
cd detector-
pip3 install -r requirements.txt
```

Cara Penggunaan

Basic Usage (2 File)

```bash
python detection_tool.py file1.txt file2.pdf
```

Multiple Files

```bash
python detection_tool.py file1.txt file2.docx file3.pdf file4.txt
```

Scan Semua File dalam Folder

```bash
python detection_tool.py folder/
```

Scan dengan Wildcard

```bash
python detection_tool.py *.txt
python detection_tool.py dokumen/*.pdf
```

Step by Step Testing

Step 1: Buat File Sample

```bash
echo "Plagiarisme adalah tindakan mengambil karya orang lain dan mengakuinya sebagai karya sendiri." > doc1.txt
echo "Plagiarisme merupakan tindakan mengambil karya milik orang lain dan mengklaim sebagai karya pribadi." > doc2.txt
echo "Hari ini saya belajar Python di Termux. Sangat menyenangkan bisa coding di HP." > doc3.txt
```

Step 2: Jalankan Deteksi

```bash
python detection_tool.py doc1.txt doc2.txt doc3.txt
```

Step 3: Lihat Hasil

```bash
cat report.json | python -m json.tool
```

Step 4: Cek Similarity Tinggi

```bash
grep -A 5 -B 5 "similar_pairs" report.json
```

Output yang Dihasilkan

report.json

Berisi similarity matrix lengkap dengan detail setiap file.

Contoh:

```json
{
  "files": ["doc1.txt", "doc2.txt", "doc3.txt"],
  "similar_pairs": [
    {
      "a": "doc1.txt",
      "b": "doc2.txt", 
      "score": 0.85
    }
  ]
}
```

suspicious.json

Berisi hasil pengecekan online (jika ada kemiripan dengan sumber internet).

Troubleshooting

Error: ModuleNotFoundError

Solusi:

```bash
pip install [nama_module]
```

Error: pandas install gagal di Termux

Solusi:

```bash
pkg install binutils
pip install pandas --no-cache-dir
```

Error: Permission denied (Linux/macOS)

Solusi:

```bash
sudo pip install -r requirements.txt
# atau
pip install --user -r requirements.txt
```

Error: pip not found (Linux)

Solusi:

```bash
sudo apt install python3-pip  # Ubuntu/Debian
sudo yum install python3-pip   # CentOS/RHEL
sudo dnf install python3-pip   # Fedora
```

Error: PdfReadError

Solusi: Skip file PDF atau pastikan file PDF tidak corrupt.

Error: MemoryError

Solusi: Kurangi jumlah file yang diproses sekaligus.

Error: No module named 'docx'

Solusi:

```bash
pip uninstall docx
pip install python-docx
```

Error: git not found

Solusi:

```bash
# Ubuntu/Debian
sudo apt install git

# Windows
Download dari https://git-scm.com/downloads

# macOS
brew install git
```

Format File yang Didukung

· .txt (Text file)
· .pdf (PDF document)
· .docx (Word document)
· .html / .htm (HTML file)

Lisensi

MIT License - Silakan gunakan, modifikasi, dan distribusikan.

Kontak

Dibuat oleh Vina - 2026

---

Happy Coding!

```
