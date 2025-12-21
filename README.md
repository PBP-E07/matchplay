# ⚽ MatchPlay

Matchplay adalah website yang membantu pengguna menemukan tempat olahraga sekaligus teman bermain di sekitar mereka. Dengan fitur matchmaking dan booking lapangan secara online, Matchplay memudahkan pemain untuk tetap aktif berolahraga, walaupun jika mereka belum memiliki teman bermain atau rekan main.

Sistem Matchmaking memungkinkan pengguna menemukan lawan atau teman bermain. Saat pengguna melakukan matchmaking, maka sistem akan menandai slot waktu lapangan sebagai pending. Jika jumlah pemain terpenuhi sebelum waktu cut off, sistem akan mengonfirmasi booking dan mengunci slot tersebut. Dengan mekanisme ini, Matchplay dapat memberikan kesempatan yang adil bagi pengguna yang bermain sendiri melalui matchmaking maupun bagi team yang siap melakukan booking secara langsung.

## 👥 Nama Anggota
- Muhammad Rifqi Ilham (2406495483)
- Valerian Hizkia Emmanuel (2406495382)
- Faris Huda (2406421970)
- Geraldus Catur Gigih Wahyudi (2406496113)
- Fathan Alfahrezi (2406496284)

## 💡 Manfaat
- Mempermudah booking lapangan secara praktis dan real-time melalui web.
- Membantu menemukan partner atau teman bermain untuk olahraga berkelompok.
- Penyewaan perlengkapan olahraga yang lebih efisien.
- Meningkatkan pendapatan pengelola lapangan.
- Sistem manajemen yang lebih terorganisir dan praktis untuk pengelola lapangan maupun penyewa lapangan.

## 🧰 Modul-Modul Matchplay
Aplikasi ini dibagi menjadi beberapa modul.

| Nama Modul | Fungsi | Pembuat |
|------------|--------|---------|
| ```main``` | Modul ini berfungsi untuk mengurus halaman utama website. | Valerian Hizkia Emmanuel |
| ```authentication``` | Modul ini nantinya akan berfungsi untuk mengurus segala macam autentikasi yang terdapat di aplikasi ini. Mau itu dari pengguna biasa ataupun pemilik lapangan. Modul ini juga nantinya mengurus perizinan (authorization) yang dimiliki oleh seorang pengguna. | Seluruh Anggota |
|```fields```| Modul ini berfungsi untuk mengurus model dari lapangan. | Faris Huda |
|```dashboard```| Modul ini berfungsi untuk mengurus segala macam hal yang berhubungan dengan lapangan. Hal-hal ini mencakup membuat, melihat, mengubah, dan menghapus lapangan yang ada (CRUD). Modul ini juga menyimpan review dan penilaian pengguna terhadap lapangan tersebut. | Faris Huda |
| ```matches``` | Modul ini berfungsi untuk menjalankan fitur matchmaking. Modul ini juga berfungsi untuk memberikan data matchmaking yang sedang berjalan. Modul ini juga nantinya akan mengurus fitur tournament antar tim. | Valerian Hizkia Emmanuel |
| ```bookings``` | Modul ini berfungsi untuk mengurus pemesanan atau peminjaman sebuah lapangan. Beda dengan matchmaking, fitur ini digunakan untuk orang yang ingin menyewa sebuah lapangan secara langsung tanpa matchmaking dengan orang lain. | Valerian Hizkia Emmanuel |
| ```tournament``` | Modul ini berfungsi untuk menjalankan fungsi turnamen. Modul ini nantinya akan mengurus anggota-anggota dari sebuah tim, nama tim, dan hal-hal lainnya yang berhubungan dengan turnamen. | Muhammad Rifqi Ilham |
| ```equipment``` | Modul ini berfungsi untuk menjalankan fungsi peminjaman alat olahraga. | Fathan Alfahrezi |
| ```blog``` | Modul ini berfungsi untuk menjalankan fungsi CRUD untuk blog pada website. | Geraldus Catur Gigih Wahyudi |

## 🖼️ Link Desain
- https://www.figma.com/design/rEODHOiReZtWyQa6pO914s/MatchPlay?node-id=0-1&t=ZTuwXxJZfQBtM5pH-1

## 📊 Sumber Initial Dataset
- Dataset lapangan didapatkan dari hasil <i>scrapping dari website</i> https://ayo.co.id/sitemap/v.xml
- Dataset customer dan perlengkapan olahraga didapat dari Dataset customer dan perlengkapan olahraga dari https://www.kaggle.com/datasets/cnezhmar/sporting-goods-store

## 👤 Tipe-Tipe Pengguna
- User, yang memiliki akses untuk mem-<i>booking</i> lapangan, melakukan <i>matchmaking</i>, dan menyewa alat.
- Admin, yang memiliki akses untuk mengatur segala hal dari melakukan <i>listing</i> lapangan dan alat sampai membatalkan <i>matchmaking</i>.
