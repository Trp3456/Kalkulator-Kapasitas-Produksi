from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)

# Fungsi-fungsi helper
def get_faktor_efisiensi_alat_excavator(kondisi_operasi_exc):
    return {
        'Mudah': 0.83,
        'Sedang': 0.75,
        'Agak sulit': 0.67,
        'Sulit': 0.58
    }.get(kondisi_operasi_exc, 0)

def get_faktor_bucket(kondisi_operasi_exc):
    return {
        'Mudah': 1.1,
        'Sedang': 1.0,
        'Agak sulit': 0.9,
        'Sulit': 0.8
    }.get(kondisi_operasi_exc, 0)

def get_faktor_konversi_galian(kondisi_galian, kondisi_dumping):
    matrix = {
        '<40%': {'Mudah': 0.7, 'Normal': 0.9, 'Agak sulit': 1.1, 'Sulit': 1.4},
        '(40-75)%': {'Mudah': 0.8, 'Normal': 1.0, 'Agak sulit': 1.3, 'Sulit': 1.6},
        '>75%': {'Mudah': 0.9, 'Normal': 1.1, 'Agak sulit': 1.5, 'Sulit': 1.8}
    }
    return matrix.get(kondisi_galian, {}).get(kondisi_dumping, 0)

def get_waktu_siklus(kapasitas_bucket, sudut_putar, kondisi_tanah):
    if kapasitas_bucket <= 0.6:
        if sudut_putar == '45-90':
            return {1: 12.7, 2: 15.25, 3: 16.6}.get(int(kondisi_tanah), 0)
        elif sudut_putar == '90-180':
            return {1: 16.5, 2: 19.8, 3: 25.3}.get(int(kondisi_tanah), 0)
    elif 0.6 < kapasitas_bucket <= 1.25:
        if sudut_putar == '45-90':
            return {1: 16.3, 2: 20.8, 3: 21.35}.get(int(kondisi_tanah), 0)
        elif sudut_putar == '90-180':
            return {1: 20.15, 2: 25.75, 3: 31.35}.get(int(kondisi_tanah), 0)
    elif 1.25 < kapasitas_bucket <= 2.2:
        if sudut_putar == '45-90':
            return {1: 18.5, 2: 23.65, 3: 28.8}.get(int(kondisi_tanah), 0)
        elif sudut_putar == '90-180':
            return {1: 22.35, 2: 28.55, 3: 34.8}.get(int(kondisi_tanah), 0)
    return 0

def get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin):
    if kondisi_operasi == 'Baik sekali':
        if pemeliharaan_mesin =='Baik sekali':
            return 0.83
        elif pemeliharaan_mesin =='Baik':
            return 0.81
        elif pemeliharaan_mesin =='Sedang':
            return 0.76
        elif pemeliharaan_mesin =='Buruk':
            return 0.70
        elif pemeliharaan_mesin =='Buruk sekali':
            return 0.63
    elif kondisi_operasi == 'Baik':
        if pemeliharaan_mesin =='Baik sekali':
            return 0.78
        elif pemeliharaan_mesin =='Baik':
            return 0.75
        elif pemeliharaan_mesin =='Sedang':
            return 0.71
        elif pemeliharaan_mesin =='Buruk':
            return 0.65
        elif pemeliharaan_mesin =='Buruk sekali':
            return 0.60
    elif kondisi_operasi == 'Sedang':
        if pemeliharaan_mesin =='Baik sekali':
            return 0.72
        elif pemeliharaan_mesin =='Baik':
            return 0.69
        elif pemeliharaan_mesin =='Sedang':
            return 0.65
        elif pemeliharaan_mesin =='Buruk':
            return 0.60
        elif pemeliharaan_mesin =='Buruk sekali':
            return 0.54
    elif kondisi_operasi == 'Buruk':
        if pemeliharaan_mesin =='Baik sekali':
            return 0.63
        elif pemeliharaan_mesin =='Baik':
            return 0.61
        elif pemeliharaan_mesin =='Sedang':
            return 0.57
        elif pemeliharaan_mesin =='Buruk':
            return 0.52
        elif pemeliharaan_mesin =='Buruk sekali':
            return 0.45
    elif kondisi_operasi == 'Buruk sekali':
        if pemeliharaan_mesin =='Baik sekali':
            return 0.53
        elif pemeliharaan_mesin =='Baik':
            return 0.50
        elif pemeliharaan_mesin =='Sedang':
            return 0.47
        elif pemeliharaan_mesin =='Buruk':
            return 0.42
        elif pemeliharaan_mesin =='Buruk sekali':
            return 0.32
    return 0

def get_faktor_efisiensi_alat_bull(kondisi_operasi):
    return {
        'Baik': 0.83,
        'Sedang': 0.75,
        'Kurang baik': 0.67,
        'Buruk': 0.58
    }.get(kondisi_operasi, 0)

def get_faktor_kemiringan(kemiringan_pisau):
    return {
        'Datar': 1,
        'Menurun': 1.2,
        'Menanjak': 0.7
    }.get(kemiringan_pisau, 0)

def get_faktor_pisau_bull(kondisi_kerja):
    return {
        'Mudah': 1,
        'Sedang': 0.8,
        'Agak sulit': 0.65,
        'Sulit': 0.5
    }.get(kondisi_kerja, 0)

def get_faktor_efisiensi_alat_dump(kondisi_kerja):
    return {
        'Baik': 0.83,
        'Sedang': 0.8,
        'Kurang baik': 0.75,
        'Buruk': 0.7
    }.get(kondisi_kerja, 0)

def get_kecepatan_isi_dump(kondisi_lapangan):
    return {
        'Datar': 40,
        'Menanjak': 20,
        'Menurun': 20
    }.get(kondisi_lapangan, 0)

def get_kecepatan_kosong_dump(kondisi_lapangan):
    return {
        'Datar': 60,
        'Menanjak': 40,
        'Menurun': 40
    }.get(kondisi_lapangan, 0)

def get_faktor_efisiensi_alat_motor(kondisi_operasi):
    return{
        1: 0.8,     # Perbaikan jalan, peralatan
        2: 0.7,     # Peminadahan
        3: 0.6,     # Penyebaran, grading
        4: 0.5      # Penggalian (trenching)
    }.get(kondisi_operasi,0)

def get_kecepatan_motor(uraian_pekerjaan):
    return{
        1: 6,   # Perbaikan jalan, peralatan
        2: 2.6, # Penyelesaian tepi sungai/ saluran (bank fininshing)
        3: 4,   # Membentuk permukaan (Fieldgrading)
        4: 4,   # Penggalian parit (trenching)
        5: 8    # Perataan permukaan (Levelling)
    }.get(uraian_pekerjaan,0)

def get_pisau_efektif(sudut_pisau, b):
    if sudut_pisau==30:
        return (b*0.5)
    elif sudut_pisau==45:
        return(b*0.5*(2^0.5))
    elif sudut_pisau==60:
        return (b*0.5*(3^0.5))
    return (b*0.5)

def get_faktor_efisiensi_alat_loader(kondisi_operasi):
    return {
        'Baik': 0.83,
        'Sedang': 0.8,
        'Kurang baik': 0.75,
        'Buruk': 0.7
    }.get(kondisi_operasi, 0)

def get_faktor_bucket_track_loader(kondisi_penumpahan):
    return {
        'Mudah': 1,
        'Sedang': 0.95,
        'Agak sulit': 0.9,
        'Sulit': 0.8
    }.get(kondisi_penumpahan, 0)

def get_waktu_siklus_standar_track_loader(cara_pengisian, kondisi_kerja, kapasitas_bucket):
    if cara_pengisian == "V-Loading":
        if kapasitas_bucket<=3:
            return {'Mudah': 0.45, 'Sedang': 0.55, 'Agak sulit': 0.7, 'Sulit':0.75}.get(kondisi_kerja, 0)
        elif kapasitas_bucket<=5:
            return {'Mudah': 0.55, 'Sedang': 0.65, 'Agak sulit': 0.7, 'Sulit':0.75}.get(kondisi_kerja, 0)
    elif cara_pengisian == "Cross Loading":
        if kapasitas_bucket<=3:
            return {'Mudah': 0.55, 'Sedang': 0.6, 'Agak sulit': 0.75, 'Sulit':0.8}.get(kondisi_kerja, 0)
        elif kapasitas_bucket<=5:
            return {'Mudah': 0.6, 'Sedang': 0.7, 'Agak sulit': 0.75, 'Sulit':0.8}.get(kondisi_kerja, 0)
    return 0

def get_waktu_siklus_standar_wheel_loader(cara_pengisian, kondisi_kerja, kapasitas_bucket):
    if cara_pengisian == "V-Loading":
        if kapasitas_bucket<=3:
            return {'Mudah': 0.45, 'Sedang': 0.55, 'Agak sulit': 0.7, 'Sulit':0.75}.get(kondisi_kerja, 0)
        elif kapasitas_bucket<=5:
            return {'Mudah': 0.55, 'Sedang': 0.65, 'Agak sulit': 0.7, 'Sulit':0.75}.get(kondisi_kerja, 0)
        elif kapasitas_bucket>=5.1:
            return {'Mudah': 0.65, 'Sedang': 0.7, 'Agak sulit': 0.75, 'Sulit':0.8}.get(kondisi_kerja, 0)
    elif cara_pengisian == "Cross Loading":
        if kapasitas_bucket<=3:
            return {'Mudah': 0.4, 'Sedang': 0.5, 'Agak sulit': 0.65, 'Sulit':0.7}.get(kondisi_kerja, 0)
        elif kapasitas_bucket<=5:
            return {'Mudah': 0.5, 'Sedang': 0.6, 'Agak sulit': 0.65, 'Sulit':0.75}.get(kondisi_kerja, 0)
        elif kapasitas_bucket>=5.1:
            return {'Mudah': 0.6, 'Sedang': 0.65, 'Agak sulit': 0.7, 'Sulit':0.75}.get(kondisi_kerja, 0)
    return 0

def get_kecepatan_loader(kondisi_kerja, kondisi):
    if kondisi=='isi':
        return {'Mudah': 23, 'Sedang': 18, 'Agak sulit': 15, 'Sulit':12}.get(kondisi_kerja, 0)
    elif kondisi=='kosong':
        return {'Mudah': 0.24, 'Sedang': 19, 'Agak sulit': 16, 'Sulit':14}.get(kondisi_kerja, 0)
    return 23  

def get_waktu_siklus_crane_lokasi(alat, lokasi):
    if alat == 'Crane (Stationary Stand By) 40 Ton':
        return{'1':33.1, '2':77.1, '3':52.2}.get(lokasi,0)
    elif alat == 'Crane (Tower), T=10-20 m, Arm 18 m, Bm 1,5 ton':
        return{'1':33.84, '2':77.84, '3':52.94}.get(lokasi,0)
    elif alat == 'Crane (Tower), T=20-40 m, Arm 30 m, Bm 2,5 ton':
        return{'1':34.81, '2':78.81, '3':53.91}.get(lokasi,0)
    return 0
def get_waktu_siklus_crane_lantai(alat, lantai):
    if alat == 'Crane (Stationary Stand By) 40 Ton':
        return{1:32.36, 2:32.86, 3:33.19, 4:33.55, 5:33.91}.get(lantai,0)
    elif alat == 'Crane (Tower), T=10-20 m, Arm 18 m, Bm 1,5 ton':
        return{6:34.06, 7:34.39, 8:34.77, 9:35.13, 10:35.46, 11:35.82}.get(lantai,0)
    elif alat == 'Crane (Tower), T=20-40 m, Arm 30 m, Bm 2,5 ton':
        return{12:35.31, 13:35.59, 14:35.87, 15:36.04, 16: 36.36, 17: 36.71, 18: 36.99, 19: 37.27, 20: 37.55, 21: 37.83, 22: 38.11, 23: 38.39, 24: 38.67, 25: 38.95, 26: 39.23, 27: 39.51, 28: 39.79}.get(lantai,0)
    return 0

# Fungsi-fungsi perhitungan untuk setiap alat
def hitung_amp(kondisi_operasi, pemeliharaan_mesin, kapasitas_alat):
    # Mendapatkan faktor efisiensi alat berdasarkan kondisi_operasi dan pemeliharaan_mesin
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat (Fa) untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Mengonversi kapasitas_alat dan faktor_efisiensi_alat ke float
    kapasitas_alat = float(kapasitas_alat)
    faktor_efisiensi_alat = float(faktor_efisiensi_alat)
    
    # Menghitung kapasitas produksi dalam ton per jam
    kapasitas_produksi = kapasitas_alat * faktor_efisiensi_alat
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging
    print(f"Debug: Kapasitas Produksi (Q) dalam ton/jam adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat dalam jam adalah {koefisien_alat}")
    
    # Mengembalikan hasil perhitungan beserta variabel dan formula yang digunakan
    return {
        'Kondisi Operasi': kondisi_operasi,
        'Pemeliharaan Mesin': pemeliharaan_mesin,
        'Kapasitas Alat': kapasitas_alat,
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (ton/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'Formula Kapasitas Produksi': 'kapasitas_alat * faktor_efisiensi_alat',
        'Formula Koefisien Alat': '1 / kapasitas_produksi'
    }


def hitung_asphalt_finisher(kondisi_operasi, pemeliharaan_mesin, v, b, D1, t, satuan):
    # Mengonversi semua input kecuali kondisi_operasi dan pemeliharaan_mesin ke float
    v = float(v)
    b = float(b)
    D1 = float(D1)
    t = float(t)
    
    # Mendapatkan faktor efisiensi alat berdasarkan kondisi_operasi dan pemeliharaan_mesin
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat (Fa) untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    if satuan == "ton/jam":
        # Menghitung kapasitas produksi dalam ton per jam
        kapasitas_produksi = v * b * 60 * faktor_efisiensi_alat * t * D1
        koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
        print(f"Debug: Kapasitas Produksi (Q) dalam ton/jam adalah {kapasitas_produksi}")
        print(f"Debug: Koefisien Alat dalam jam adalah {koefisien_alat}")
        return {
            'Kondisi Operasi': kondisi_operasi,
            'Pemeliharaan Mesin': pemeliharaan_mesin,
            'Kecepatan, v': v,
            'Lebar, b': b,
            'Diameter, D1': D1,
            'Tinggi, t': t,
            'Satuan': satuan,
            'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
            'Kapasitas Produksi, Q (ton/jam)': kapasitas_produksi,
            'Koefisien Alat (jam)': koefisien_alat,
            'Formula Kapasitas Produksi': 'v * b * 60 * faktor_efisiensi_alat * t * D1',
            'Formula Koefisien Alat': '1 / kapasitas_produksi'
        }
    elif satuan == "m3/jam":
        # Menghitung kapasitas produksi dalam meter kubik per jam
        kapasitas_produksi = v * b * 60 * faktor_efisiensi_alat * t
        koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
        print(f"Debug: Kapasitas Produksi (Q) dalam m3/jam adalah {kapasitas_produksi}")
        print(f"Debug: Koefisien Alat dalam jam adalah {koefisien_alat}")
        return {
            'Kondisi Operasi': kondisi_operasi,
            'Pemeliharaan Mesin': pemeliharaan_mesin,
            'Kecepatan, v': v,
            'Lebar, b': b,
            'Diameter, D1': D1,
            'Tinggi, t': t,
            'Satuan': satuan,
            'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
            'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
            'Koefisien Alat (jam)': koefisien_alat,
            'Formula Kapasitas Produksi': 'v * b * 60 * faktor_efisiensi_alat * t',
            'Formula Koefisien Alat': '1 / kapasitas_produksi'
        }
    elif satuan == "m2/jam":
        # Menghitung kapasitas produksi dalam meter persegi per jam
        kapasitas_produksi = v * b * 60 * faktor_efisiensi_alat
        koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
        print(f"Debug: Kapasitas Produksi (Q) dalam m2/jam adalah {kapasitas_produksi}")
        print(f"Debug: Koefisien Alat dalam jam adalah {koefisien_alat}")
        return {
            'Kondisi Operasi': kondisi_operasi,
            'Pemeliharaan Mesin': pemeliharaan_mesin,
            'Kecepatan, v': v,
            'Lebar, b': b,
            'Diameter, D1': D1,
            'Tinggi, t': t,
            'Satuan': satuan,
            'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
            'Kapasitas Produksi, Q (m2/jam)': kapasitas_produksi,
            'Koefisien Alat (jam)': koefisien_alat,
            'Formula Kapasitas Produksi': 'v * b * 60 * faktor_efisiensi_alat',
            'Formula Koefisien Alat': '1 / kapasitas_produksi'
        }
    return 0


def hitung_asphalt_sprayer(kondisi_operasi, pemeliharaan_mesin, Pa, lt, satuan):
    # Mengonversi semua input kecuali kondisi_operasi dan pemeliharaan_mesin ke float
    Pa = float(Pa)
    lt = float(lt)

    # Mendapatkan faktor efisiensi alat berdasarkan kondisi_operasi dan pemeliharaan_mesin
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat (Fa) untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    if satuan == "liter/jam":
        # Menghitung kapasitas produksi dalam liter per jam
        kapasitas_produksi = Pa * 60 * faktor_efisiensi_alat
        koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
        print(f"Debug: Kapasitas Produksi (Q) dalam liter/jam adalah {kapasitas_produksi}")
        print(f"Debug: Koefisien Alat dalam jam adalah {koefisien_alat}")
        return {
            'Kondisi Operasi': kondisi_operasi,
            'Pemeliharaan Mesin': pemeliharaan_mesin,
            'Pa': Pa,
            'lt': lt,
            'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
            'Kapasitas Produksi, Q (liter/jam)': kapasitas_produksi,
            'Koefisien Alat (jam)': koefisien_alat,
            'Formula Kapasitas Produksi': 'Pa * 60 * faktor_efisiensi_alat',
            'Formula Koefisien Alat': '1 / kapasitas_produksi'
        }
    elif satuan == "m2/jam":
        # Menghitung kapasitas produksi dalam meter persegi per jam
        kapasitas_produksi = Pa * 60 * faktor_efisiensi_alat / lt
        koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
        print(f"Debug: Kapasitas Produksi (Q) dalam m2/jam adalah {kapasitas_produksi}")
        print(f"Debug: Koefisien Alat dalam jam adalah {koefisien_alat}")
        return {
            'Kondisi Operasi': kondisi_operasi,
            'Pemeliharaan Mesin': pemeliharaan_mesin,
            'Pa': Pa,
            'lt': lt,
            'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
            'Kapasitas Produksi, Q (m2/jam)': kapasitas_produksi,
            'Koefisien Alat (jam)': koefisien_alat,
            'Formula Kapasitas Produksi': 'Pa * 60 * faktor_efisiensi_alat / lt',
            'Formula Koefisien Alat': '1 / kapasitas_produksi'
        }
    return 0

def hitung_bulldozer(kondisi_operasi, kondisi_kerja, b, bo, W, n, H, kemiringan_pisau, vF, vR, l, jenis_transmisi):
    # Mengonversi semua input kecuali kondisi_operasi, kondisi_kerja, dan jenis_transmisi ke float
    b = float(b)
    bo = float(bo)
    W = float(W)
    n = float(n)
    H = float(H)
    kemiringan_pisau = float(kemiringan_pisau)
    vF = float(vF)
    vR = float(vR)
    l = float(l)

    # Mendapatkan faktor-faktor yang diperlukan
    faktor_efisiensi_alat = get_faktor_efisiensi_alat_bull(kondisi_operasi)
    faktor_pisau = get_faktor_pisau_bull(kondisi_kerja)
    faktor_kemiringan = get_faktor_kemiringan(kemiringan_pisau)

    # Menghitung kapasitas dan parameter lainnya
    kapasitas_pisau = b * H * H
    lebar_lintasan_pengupasan = b - bo
    jumlah_lajur_lintasan = W / lebar_lintasan_pengupasan

    if jenis_transmisi == "Direct Drive (DD)":
        waktu_pasti = 0.1
    else:
        waktu_pasti = 0.05

    T1 = (l * 60 / vF)
    T2 = (l * 60 / vR)
    waktu_siklus = waktu_pasti + T1 + T2

    kapasitas_produksi_m3 = kapasitas_pisau * faktor_pisau * faktor_efisiensi_alat * faktor_kemiringan * 60 / waktu_siklus
    koefisien_alat_m3 = 1 / kapasitas_produksi_m3 if kapasitas_produksi_m3 else 0

    kapasitas_produksi_m2 = l * (jumlah_lajur_lintasan * lebar_lintasan_pengupasan + bo) * faktor_pisau * faktor_efisiensi_alat * faktor_kemiringan * 60 / (jumlah_lajur_lintasan * n * waktu_siklus)
    koefisien_alat_m2 = 1 / kapasitas_produksi_m2 if kapasitas_produksi_m2 else 0

    # Debug statements to check intermediate values
    print(f"Debug: Faktor Efisiensi Alat (Fa) untuk kondisi operasi {kondisi_operasi} adalah {faktor_efisiensi_alat}")
    print(f"Debug: Faktor Pisau (Fb) untuk kondisi kerja {kondisi_kerja} adalah {faktor_pisau}")
    print(f"Debug: Faktor Kemiringan (Fm) untuk kemiringan pisau {kemiringan_pisau} adalah {faktor_kemiringan}")
    print(f"Debug: Kapasitas Pisau (q) adalah {kapasitas_pisau}")
    print(f"Debug: Lebar Lintasan Pengupasan (b_ef) adalah {lebar_lintasan_pengupasan}")
    print(f"Debug: Jumlah Lajur Lintasan (N) adalah {jumlah_lajur_lintasan}")
    print(f"Debug: Waktu Menodorong (T1) adalah {T1} menit")
    print(f"Debug: Waktu Mundur (T2) adalah {T2} menit")
    print(f"Debug: Waktu Pasti (Z) adalah {waktu_pasti} menit")
    print(f"Debug: Waktu Siklus (Ts) adalah {waktu_siklus} menit")
    print(f"Debug: Kapasitas Produksi (Q) dalam m3/jam adalah {kapasitas_produksi_m3}")
    print(f"Debug: Koefisien Alat (jam/m3) adalah {koefisien_alat_m3}")
    print(f"Debug: Kapasitas Produksi (Q) dalam m2/jam adalah {kapasitas_produksi_m2}")
    print(f"Debug: Koefisien Alat (jam/m2) adalah {koefisien_alat_m2}")

    return {
        'Faktor Efisiensi Alat Bulldozer, Fa bull': faktor_efisiensi_alat,
        'Faktor Kemiringan, Fm': faktor_kemiringan,
        'Faktor Pisau, Fb': faktor_pisau,
        'Kapasitas Pisau, q (m3)': kapasitas_pisau,
        'Lebar Lintasan Pengupasan, b_ef': lebar_lintasan_pengupasan,
        'Jumlah Lajur Lintasan Pengupasan, N': jumlah_lajur_lintasan,
        'Waktu Menodorong, T1 (menit)': T1,
        'Waktu Mundur, T2 (menit)': T2,
        'Waktu Pasti, Z (menit)': waktu_pasti,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi_m3,
        'Koefisien Alat (jam/m3)': koefisien_alat_m3,
        'Kapasitas Produksi, Q (m2/jam)': kapasitas_produksi_m2,
        'Koefisien Alat (jam/m2)': koefisien_alat_m2,
        'Formula Kapasitas Produksi m3': 'kapasitas_pisau * faktor_pisau * faktor_efisiensi_alat * faktor_kemiringan * 60 / waktu_siklus',
        'Formula Koefisien Alat m3': '1 / kapasitas_produksi_m3',
        'Formula Kapasitas Produksi m2': 'l * (jumlah_lajur_lintasan * lebar_lintasan_pengupasan + bo) * faktor_pisau * faktor_efisiensi_alat * faktor_kemiringan * 60 / (jumlah_lajur_lintasan * n * waktu_siklus)',
        'Formula Koefisien Alat m2': '1 / kapasitas_produksi_m2'
    }

def hitung_air_compressor(kondisi_operasi, pemeliharaan_mesin, penggunaan, kapasitas_alat):
    # Mengonversi kapasitas_alat ke float
    kapasitas_alat = float(kapasitas_alat)

    # Mendapatkan faktor efisiensi alat berdasarkan kondisi_operasi dan pemeliharaan_mesin
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat (Fa) untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    if penggunaan == "Jack Hammer":
        # Menghitung kapasitas produksi dalam m3/jam untuk penggunaan Jack Hammer
        kapasitas_produksi = kapasitas_alat * faktor_efisiensi_alat * 60
        koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
        print(f"Debug: Kapasitas Produksi (Q) dalam m3/jam adalah {kapasitas_produksi}")
        print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")
        return {
            'Faktor Efisiensi Alat': faktor_efisiensi_alat,
            'Kapasitas_alat': kapasitas_alat,
            'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
            'Koefisien Alat (jam)': koefisien_alat
        }
    else:
        # Menghitung kapasitas produksi dalam m2/jam untuk penggunaan selain Jack Hammer
        kapasitas_produksi = kapasitas_alat * faktor_efisiensi_alat * 60
        koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
        print(f"Debug: Kapasitas Produksi (Q) dalam m2/jam adalah {kapasitas_produksi}")
        print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")
        return {
            'Faktor Efisiensi Alat': faktor_efisiensi_alat,
            'Kapasitas_alat': kapasitas_alat,
            'Kapasitas Produksi, Q (m2/jam)': kapasitas_produksi,
            'Koefisien Alat (jam)': koefisien_alat
        }

def hitung_concrete_mixer(kondisi_operasi, pemeliharaan_mesin, Cp, T1, T2, T3, T4):
    # Mengonversi input ke float
    Cp = float(Cp)
    T1 = float(T1)
    T2 = float(T2)
    T3 = float(T3)
    T4 = float(T4)
    
    # Mendapatkan faktor efisiensi alat berdasarkan kondisi_operasi dan pemeliharaan_mesin
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat (Fa) untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Menghitung waktu siklus
    waktu_siklus = T1 + T2 + T3 + T4
    print(f"Debug: Waktu Siklus (Ts) adalah {waktu_siklus} menit")
    
    # Menghitung kapasitas produksi
    kapasitas_produksi = Cp * faktor_efisiensi_alat * 60 / (1000 * waktu_siklus)
    print(f"Debug: Kapasitas Produksi (Q) dalam m3/jam adalah {kapasitas_produksi}")
    
    # Menghitung koefisien alat
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")
    
    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'T1 (menit)': T1,
        'T2 (menit)': T2,
        'T3 (menit)': T3,
        'T4 (menit)': T4,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'Formula Waktu Siklus': 'Waktu Siklus, Ts = T1 + T2 + T3 + T4',
        'Formula Kapasitas Produksi': 'Kapasitas Produksi, Q = Cp * Fa * 60 / (1000 * Ts)',
        'Formula Koefisien Alat': 'Koefisien Alat = 1 / Q' if kapasitas_produksi else 'Koefisien Alat tidak terdefinisi'
    }

# hitung_crane_10-15 ton juga digunakan untuk Crane On Track (Crawler Crane) 75 Ton, crane on Track 75-100 ton
def hitung_crane_10_15_ton(kondisi_operasi, pemeliharaan_mesin, V, T1, T2):
    # Mengonversi input ke float
    V = float(V)
    T1 = float(T1)
    T2 = float(T2)
    
    # Mendapatkan faktor efisiensi alat berdasarkan kondisi_operasi dan pemeliharaan_mesin
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat (Fa) untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Menghitung waktu siklus
    waktu_siklus = T1 + T2
    print(f"Debug: Waktu Siklus (Ts) adalah {waktu_siklus} menit")
    
    # Menghitung kapasitas produksi
    kapasitas_produksi = V * faktor_efisiensi_alat * 60 / waktu_siklus
    print(f"Debug: Kapasitas Produksi (Q) dalam buah/jam adalah {kapasitas_produksi}")
    
    # Menghitung koefisien alat
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")
    
    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'T1 (menit)': T1,
        'T2 (menit)': T2,
        'Kapasitas Produksi, Q (buah/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'Formula Waktu Siklus': 'Waktu Siklus, Ts = T1 + T2',
        'Formula Kapasitas Produksi': 'Kapasitas Produksi, Q = V * Fa * 60 / Ts',
        'Formula Koefisien Alat': 'Koefisien Alat = 1 / Q' if kapasitas_produksi else 'Koefisien Alat tidak terdefinisi'
    }

# hitung_dump_truck juga digunakan untuk dump truck, truck semi trailer
def hitung_dump_truck(kondisi_kerja, kondisi_lapangan, V, BiL, L, T1, T4):
    # Mendapatkan faktor efisiensi alat dan kecepatan isi serta kosong dari fungsi-fungsi terkait
    faktor_efisiensi_alat = float(get_faktor_efisiensi_alat_dump(kondisi_kerja))
    vF = float(get_kecepatan_isi_dump(kondisi_lapangan))
    vR = float(get_kecepatan_kosong_dump(kondisi_lapangan))
    
    # Mengonversi semua input ke float
    V = float(V)
    BiL = float(BiL)
    L = float(L)
    T1 = float(T1)
    T4 = float(T4)
    
    # Menghitung waktu tempuh isi dan kosong dalam menit
    waktu_tempuh_isi = L * 60 / vF
    waktu_tempuh_kosong = L * 60 / vR
    
    # Menghitung waktu siklus
    waktu_siklus = T1 + waktu_tempuh_isi + waktu_tempuh_kosong + T4
    print(f"Debug: Waktu Tempuh Isi (T2) adalah {waktu_tempuh_isi} menit")
    print(f"Debug: Waktu Tempuh Kosong (T3) adalah {waktu_tempuh_kosong} menit")
    print(f"Debug: Waktu Siklus (Ts) adalah {waktu_siklus} menit")
    
    # Menghitung kapasitas produksi
    kapasitas_produksi = V * faktor_efisiensi_alat * 60 / (BiL * waktu_siklus)
    print(f"Debug: Kapasitas Produksi (Q) dalam m3/jam adalah {kapasitas_produksi}")
    
    # Menghitung koefisien alat
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")
    
    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kecepatan Isi, vF (m/min)': vF,
        'Kecepatan Kosong, vR (m/min)': vR,
        'Volume, V (m3)': V,
        'Lebar Isian, BiL (m)': BiL,
        'Jarak Tempuh, L (m)': L,
        'Waktu Tempuh Isi, T2 (menit)': waktu_tempuh_isi,
        'Waktu Tempuh Kosong, T3 (menit)': waktu_tempuh_kosong,
        'Waktu Pasti, T1 (menit)': T1,
        'Waktu Kosong, T4 (menit)': T4,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam/m3)': koefisien_alat,
        'Formula Waktu Tempuh Isi': 'Waktu Tempuh Isi, T2 = (L * 60) / vF',
        'Formula Waktu Tempuh Kosong': 'Waktu Tempuh Kosong, T3 = (L * 60) / vR',
        'Formula Waktu Siklus': 'Waktu Siklus, Ts = T1 + T2 + T3 + T4',
        'Formula Kapasitas Produksi': 'Kapasitas Produksi, Q = (V * Fa * 60) / (BiL * Ts)',
        'Formula Koefisien Alat': 'Koefisien Alat = 1 / Q' if kapasitas_produksi else 'Koefisien Alat tidak terdefinisi'
    }

def hitung_excavator(kondisi_operasi_exc, kondisi_galian, kondisi_dumping, kapasitas_bucket, sudut_putar, kondisi_tanah):
    # Mendapatkan faktor efisiensi alat, bucket, dan konversi galian
    faktor_efisiensi_alat = float(get_faktor_efisiensi_alat_excavator(kondisi_operasi_exc))
    faktor_bucket = float(get_faktor_bucket(kondisi_operasi_exc))
    faktor_konversi_galian = float(get_faktor_konversi_galian(kondisi_galian, kondisi_dumping))
    
    # Mengonversi kapasitas bucket dan kondisi tanah ke float dan int
    kapasitas_bucket = float(kapasitas_bucket)
    sudut_putar = float(sudut_putar)
    kondisi_tanah = int(kondisi_tanah)
    
    # Menghitung waktu siklus
    waktu_siklus = get_waktu_siklus(kapasitas_bucket, sudut_putar, kondisi_tanah)
    
    # Debug statement
    print(f"Debug: Faktor Efisiensi Alat (Fa) = {faktor_efisiensi_alat}")
    print(f"Debug: Faktor Bucket (Fb) = {faktor_bucket}")
    print(f"Debug: Faktor Konversi Galian (Fg) = {faktor_konversi_galian}")
    print(f"Debug: Waktu Siklus (detik) = {waktu_siklus}")

    if waktu_siklus <= 0 or faktor_konversi_galian <= 0:
        return {'error': 'Data input tidak valid untuk perhitungan excavator'}
    
    # Menghitung kapasitas produksi dan koefisien alat
    kapasitas_produksi = (kapasitas_bucket * faktor_efisiensi_alat * faktor_bucket * 60) / (faktor_konversi_galian * waktu_siklus / 60)
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debug statement
    print(f"Debug: Kapasitas Produksi (Q) = {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) = {koefisien_alat}")
    
    return {
        'Faktor Efisiensi Alat': faktor_efisiensi_alat,
        'Faktor Bucket': faktor_bucket,
        'Faktor Konversi Galian': faktor_konversi_galian,
        'Waktu Siklus (detik)': waktu_siklus,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'Formula Waktu Siklus': 'Waktu Siklus (detik) = get_waktu_siklus(kapasitas_bucket, sudut_putar, kondisi_tanah)',
        'Formula Kapasitas Produksi': 'Kapasitas Produksi, Q = (kapasitas_bucket * faktor_efisiensi_alat * faktor_bucket * 60) / (faktor_konversi_galian * waktu_siklus / 60)',
        'Formula Koefisien Alat': 'Koefisien Alat = 1 / kapasitas_produksi' if kapasitas_produksi else 'Koefisien Alat tidak terdefinisi'
    }

def hitung_flat_bed_truck(kondisi_operasi, pemeliharaan_mesin, kapasitas_alat, jarak_lokasi, kecepatan_bermuatan, kecepatan_kosong, waktu_muat, waktu_bongkar):
    # Mengonversi semua input ke tipe float
    faktor_efisiensi_alat = float(get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin))
    kapasitas_alat = float(kapasitas_alat)
    jarak_lokasi = float(jarak_lokasi)
    kecepatan_bermuatan = float(kecepatan_bermuatan)
    kecepatan_kosong = float(kecepatan_kosong)
    waktu_muat = float(waktu_muat)
    waktu_bongkar = float(waktu_bongkar)
    
    # Validasi data input
    if faktor_efisiensi_alat <= 0 or jarak_lokasi <= 0 or kecepatan_bermuatan <= 0 or kecepatan_kosong <= 0 or waktu_muat <= 0 or waktu_bongkar <= 0:
        return {'error': 'Data input tidak valid untuk perhitungan flat bed truck'}
    
    # Menghitung waktu perjalanan muatan
    waktu_perjalanan_muatan = jarak_lokasi / kecepatan_bermuatan
    
    # Menghitung waktu perjalanan kosong
    waktu_perjalanan_kosong = jarak_lokasi / kecepatan_kosong
    
    # Menghitung waktu siklus
    waktu_siklus = waktu_muat + waktu_bongkar + waktu_perjalanan_muatan + waktu_perjalanan_kosong
    
    # Menghitung kapasitas produksi
    kapasitas_produksi = (kapasitas_alat * faktor_efisiensi_alat * 60) / waktu_siklus
    
    # Menghitung koefisien alat
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debug statements
    print(f"Debug: Faktor Efisiensi Alat (Fa) = {faktor_efisiensi_alat}")
    print(f"Debug: Kapasitas Alat = {kapasitas_alat}")
    print(f"Debug: Jarak Lokasi = {jarak_lokasi}")
    print(f"Debug: Kecepatan Bermuatan = {kecepatan_bermuatan}")
    print(f"Debug: Kecepatan Kosong = {kecepatan_kosong}")
    print(f"Debug: Waktu Muat = {waktu_muat}")
    print(f"Debug: Waktu Bongkar = {waktu_bongkar}")
    print(f"Debug: Waktu Perjalanan Muatan = {waktu_perjalanan_muatan}")
    print(f"Debug: Waktu Perjalanan Kosong = {waktu_perjalanan_kosong}")
    print(f"Debug: Waktu Siklus = {waktu_siklus}")
    print(f"Debug: Kapasitas Produksi (Q) = {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) = {koefisien_alat}")
    
    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kapasitas Alat': kapasitas_alat,
        'Jarak Lokasi': jarak_lokasi,
        'Kecepatan Bermuatan': kecepatan_bermuatan,
        'Kecepatan Kosong': kecepatan_kosong,
        'Waktu Muat': waktu_muat,
        'Waktu Bongkar': waktu_bongkar,
        'Waktu Perjalanan Muatan (menit)': waktu_perjalanan_muatan,
        'Waktu Perjalanan Kosong (menit)': waktu_perjalanan_kosong,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'Formula Kapasitas Produksi': 'Kapasitas Produksi, Q = (kapasitas_alat * faktor_efisiensi_alat * 60) / waktu_siklus',
        'Formula Waktu Siklus': 'Waktu Siklus, Ts = waktu_muat + waktu_bongkar + waktu_perjalanan_muatan + waktu_perjalanan_kosong',
        'Formula Koefisien Alat': 'Koefisien Alat = 1 / kapasitas_produksi' if kapasitas_produksi else 'Koefisien Alat tidak terdefinisi'
    }

def hitung_generating_set(kondisi_operasi, pemeliharaan_mesin, V):
    # Konversi input ke float
    V = float(V)

    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat (Fa) untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")

    # Menghitung kapasitas produksi dan koefisien alat
    kapasitas_produksi = faktor_efisiensi_alat * V
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0

    # Debug output
    print(f"Debug: Kapasitas Produksi (Q) adalah {kapasitas_produksi} kW/jam")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (kW/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'Input Kapasitas Alat, V': V,
        'Formula Kapasitas Produksi': 'Faktor Efisiensi Alat * V',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi'
    }

def hitung_motor_grader(kondisi_operasi, uraian_pekerjaan, Lh, sudut_pisau, b, bo, n, W, T2):
    # Konversi semua input ke float
    Lh = float(Lh)
    sudut_pisau = float(sudut_pisau)
    b = float(b)
    bo = float(bo)
    W = float(W)
    T2 = float(T2)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat_motor(kondisi_operasi)
    print(f"Debug: Faktor Efisiensi Alat Motor Grader (Fa MG) untuk kondisi operasi {kondisi_operasi} adalah {faktor_efisiensi_alat}")
    
    # Mendapatkan kecepatan motor dan lebar pisau efektif
    kecepatan = get_kecepatan_motor(uraian_pekerjaan)
    be = get_pisau_efektif(sudut_pisau, b)
    
    # Menghitung jumlah lajur lintasan dan waktu siklus
    jumlah_lajur_lintasan = W / (be - bo)
    T1 = Lh * 60 / (kecepatan * 1000)
    waktu_siklus = T1 + T2
    
    # Menghitung kapasitas produksi dan koefisien alat
    kapasitas_produksi = Lh * (jumlah_lajur_lintasan * (be - bo) + bo) * faktor_efisiensi_alat * 60 / waktu_siklus
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debug output
    print(f"Debug: Kecepatan Motor Grader adalah {kecepatan} km/jam")
    print(f"Debug: Lebar Pisau Efektif (b_ef) adalah {be} meter")
    print(f"Debug: Jumlah Lajur Lintasan Pengupasan (N) adalah {jumlah_lajur_lintasan}")
    print(f"Debug: Waktu 1 kali lintasan (T1) adalah {T1} menit")
    print(f"Debug: Waktu Siklus (Ts) adalah {waktu_siklus} menit")
    print(f"Debug: Kapasitas Produksi (Q) adalah {kapasitas_produksi} m3/jam")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")

    if jumlah_lajur_lintasan > 1:
        return {
            'Faktor Efisiensi Alat Motor Grader, Fa MG': faktor_efisiensi_alat,
            'Lebar Pisau Efektif, b_ef': be,
            'Jumlah Lajur Lintasan Pengupasan, N': jumlah_lajur_lintasan,
            'Waktu 1 kali lintasan, T1 (menit)': T1,
            'Waktu Siklus, Ts (menit)': waktu_siklus,
            'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
            'Koefisien Alat (jam)': koefisien_alat,
            'Input Lebar Pisau, b': b,
            'Input Lebar Area Pekerjaan, W': W,
            'Formula Jumlah Lajur Lintasan': 'W / (Lebar Pisau Efektif - bo)',
            'Formula Waktu 1 Kali Lintasan (T1)': 'Lh * 60 / (kecepatan * 1000)',
            'Formula Waktu Siklus': 'T1 + T2',
            'Formula Kapasitas Produksi': 'Lh * (Jumlah Lajur Lintasan * (Lebar Pisau Efektif - bo) + bo) * Faktor Efisiensi Alat * 60 / Waktu Siklus',
            'Formula Koefisien Alat': '1 / Kapasitas Produksi'
        }
    else:
        return {'error': 'Panjang pisau (b) perlu disesuaikan dengan lebar area pekerjaan (W) agar nilai N menjadi lebih dari 1'}
  
def hitung_track_loader(kondisi_operasi, kondisi_penumpahan, kondisi_kerja, cara_pengisian, kapasitas_bucket, jarak_pergerakan, L, Z):
    # Konversi semua input yang relevan ke float
    kapasitas_bucket = float(kapasitas_bucket)
    L = float(L)
    Z = float(Z)
    
    # Mendapatkan faktor efisiensi alat dan faktor bucket
    faktor_efisiensi_alat = get_faktor_efisiensi_alat_loader(kondisi_operasi)
    faktor_bucket = get_faktor_bucket(kondisi_penumpahan)
    print(f"Debug: Faktor Efisiensi Alat Track Loader (Fa TL) untuk kondisi operasi {kondisi_operasi} adalah {faktor_efisiensi_alat}")
    print(f"Debug: Faktor Bucket (Fb) untuk kondisi penumpahan {kondisi_penumpahan} adalah {faktor_bucket}")

    # Mendapatkan waktu siklus standar dan kecepatan
    waktu_siklus_standar = get_waktu_siklus_standar_track_loader(cara_pengisian, kondisi_kerja, kapasitas_bucket)  
    kecepatan_bermuatan = get_kecepatan_loader(kondisi_kerja, 'isi')
    kecepatan_kosong = get_kecepatan_loader(kondisi_kerja, 'kosong')
    print(f"Debug: Waktu Siklus Standar (Ts) adalah {waktu_siklus_standar}")
    print(f"Debug: Kecepatan Bermuatan (vF) adalah {kecepatan_bermuatan} km/jam")
    print(f"Debug: Kecepatan Kosong (vR) adalah {kecepatan_kosong} km/jam")
    
    # Menghitung waktu tempuh dan waktu siklus
    waktu_tempuh_isi = L * 60 / kecepatan_bermuatan
    waktu_tempuh_kosong = L * 60 / kecepatan_kosong
    waktu_siklus = waktu_tempuh_isi + waktu_tempuh_kosong + Z
    
    # Menghitung kapasitas produksi dan koefisien alat
    if jarak_pergerakan == 'Dekat':
        kapasitas_produksi = kapasitas_bucket * faktor_efisiensi_alat * faktor_bucket * 60 / waktu_siklus_standar
        koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
        return {
            'Faktor Efisiensi Alat Track Loader, Fa TL': faktor_efisiensi_alat,
            'Faktor Bucket, Fb': faktor_bucket,
            'Waktu Siklus Standar, Ts (menit)': waktu_siklus_standar,
            'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
            'Koefisien Alat (jam)': koefisien_alat,
            'Input Kapasitas Bucket': kapasitas_bucket,
            'Formula Kapasitas Produksi Dekat': 'Kapasitas Bucket * Faktor Efisiensi Alat * Faktor Bucket * 60 / Waktu Siklus Standar'
        }
    elif jarak_pergerakan == 'Jauh':
        kapasitas_produksi = kapasitas_bucket * faktor_efisiensi_alat * faktor_bucket * 60 / waktu_siklus
        koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
        return {
            'Faktor Efisiensi Alat Track Loader, Fa TL': faktor_efisiensi_alat,
            'Faktor Bucket, Fb': faktor_bucket,
            'Kecepatan Bermuatan, vF (km/jam)': kecepatan_bermuatan,
            'Kecepatan Kosong, vR (km/jam)': kecepatan_kosong,
            'Waktu Tempuh Bermuatan, T1 (menit)': waktu_tempuh_isi,
            'Waktu Tempuh Kosong, T2 (menit)': waktu_tempuh_kosong,
            'Waktu Siklus, Ts (menit)': waktu_siklus,
            'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
            'Koefisien Alat (jam)': koefisien_alat,
            'Formula Kapasitas Produksi Jauh': 'Kapasitas Bucket * Faktor Efisiensi Alat * Faktor Bucket * 60 / Waktu Siklus',
            'Formula Waktu Tempuh Bermuatan (T1)': 'L * 60 / Kecepatan Bermuatan',
            'Formula Waktu Tempuh Kosong (T2)': 'L * 60 / Kecepatan Kosong',
            'Formula Waktu Siklus': 'Waktu Tempuh Bermuatan + Waktu Tempuh Kosong + Z',
            'Formula Koefisien Alat': '1 / Kapasitas Produksi'
        }
    return 0

def hitung_wheel_loader(kondisi_operasi, kondisi_penumpahan, kondisi_kerja, cara_pengisian, kapasitas_bucket, jarak_pergerakan, L, Z):
    # Konversi semua input yang relevan ke float
    kapasitas_bucket = float(kapasitas_bucket)
    L = float(L)
    Z = float(Z)

    # Mendapatkan faktor efisiensi alat dan faktor bucket
    faktor_efisiensi_alat = get_faktor_efisiensi_alat_loader(kondisi_operasi)
    faktor_bucket = get_faktor_bucket(kondisi_penumpahan)
    print(f"Debug: Faktor Efisiensi Alat Wheel Loader (Fa WL) untuk kondisi operasi {kondisi_operasi} adalah {faktor_efisiensi_alat}")
    print(f"Debug: Faktor Bucket (Fb) untuk kondisi penumpahan {kondisi_penumpahan} adalah {faktor_bucket}")

    # Mendapatkan waktu siklus standar dan kecepatan
    waktu_siklus_standar = get_waktu_siklus_standar_wheel_loader(cara_pengisian, kondisi_kerja, kapasitas_bucket)  
    kecepatan_bermuatan = get_kecepatan_loader(kondisi_kerja, 'isi')
    kecepatan_kosong = get_kecepatan_loader(kondisi_kerja, 'kosong')
    print(f"Debug: Waktu Siklus Standar (Ts) adalah {waktu_siklus_standar}")
    print(f"Debug: Kecepatan Bermuatan (vF) adalah {kecepatan_bermuatan} km/jam")
    print(f"Debug: Kecepatan Kosong (vR) adalah {kecepatan_kosong} km/jam")
    
    # Menghitung waktu tempuh dan waktu siklus
    waktu_tempuh_isi = L * 60 / kecepatan_bermuatan
    waktu_tempuh_kosong = L * 60 / kecepatan_kosong
    waktu_siklus = waktu_tempuh_isi + waktu_tempuh_kosong + Z
    
    # Menghitung kapasitas produksi dan koefisien alat
    if jarak_pergerakan == 'Dekat':
        kapasitas_produksi = kapasitas_bucket * faktor_efisiensi_alat * faktor_bucket * 60 / waktu_siklus_standar
        koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
        return {
            'Faktor Efisiensi Alat Wheel Loader, Fa WL': faktor_efisiensi_alat,
            'Faktor Bucket, Fb': faktor_bucket,
            'Waktu Siklus Standar, Ts (menit)': waktu_siklus_standar,
            'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
            'Koefisien Alat (jam)': koefisien_alat,
            'Input Kapasitas Bucket': kapasitas_bucket,
            'Formula Kapasitas Produksi Dekat': 'Kapasitas Bucket * Faktor Efisiensi Alat * Faktor Bucket * 60 / Waktu Siklus Standar'
        }
    elif jarak_pergerakan == 'Jauh':
        kapasitas_produksi = kapasitas_bucket * faktor_efisiensi_alat * faktor_bucket * 60 / waktu_siklus
        koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
        return {
            'Faktor Efisiensi Alat Wheel Loader, Fa WL': faktor_efisiensi_alat,
            'Faktor Bucket, Fb': faktor_bucket,
            'Kecepatan Bermuatan, vF (km/jam)': kecepatan_bermuatan,
            'Kecepatan Kosong, vR (km/jam)': kecepatan_kosong,
            'Waktu Tempuh Bermuatan, T1 (menit)': waktu_tempuh_isi,
            'Waktu Tempuh Kosong, T2 (menit)': waktu_tempuh_kosong,
            'Waktu Siklus, Ts (menit)': waktu_siklus,
            'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
            'Koefisien Alat (jam)': koefisien_alat,
            'Formula Kapasitas Produksi Jauh': 'Kapasitas Bucket * Faktor Efisiensi Alat * Faktor Bucket * 60 / Waktu Siklus',
            'Formula Waktu Tempuh Bermuatan (T1)': 'L * 60 / Kecepatan Bermuatan',
            'Formula Waktu Tempuh Kosong (T2)': 'L * 60 / Kecepatan Kosong',
            'Formula Waktu Siklus': 'Waktu Tempuh Bermuatan + Waktu Tempuh Kosong + Z',
            'Formula Koefisien Alat': '1 / Kapasitas Produksi'
        }
    return 0

# hitung_TWR digunakan untuk TWR dan Tandem Roller
def hitung_TWR(kondisi_operasi, pemeliharaan_mesin, v, t, b, bo, n, W):
    # Konversi semua input yang relevan ke float
    v = float(v)
    t = float(t)
    b = float(b)
    bo = float(bo)
    n = float(n)
    W = float(W)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat (Fa) untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Menghitung lebar efektif dan jumlah lajur lintasan
    v = 2
    bo = 0.2
    be = b - bo
    N = W / be
    print(f"Debug: Lebar Efektif Pemadatan (be) adalah {be}")
    print(f"Debug: Jumlah Lajur Lintasan (N) adalah {N}")
    
    # Menghitung kapasitas produksi dan koefisien alat
    kapasitas_produksi = (N * be + bo) * v* 1000 * faktor_efisiensi_alat * t / (N * n)
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Kapasitas Produksi (Q) adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")

    if N > b:
        return {
            'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
            'Lebar Efektif Pemadatan, be (m)': be,
            'Jumlah Lajur Lintasan, N': N,
            'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
            'Koefisien Alat (jam)': koefisien_alat,
            'Formula Kapasitas Produksi': '(N * be + bo) * v * 1000 * Faktor Efisiensi Alat * t / (N * n)',
            'Formula Lebar Efektif Pemadatan (be)': 'b - bo',
            'Formula Jumlah Lajur Lintasan (N)': 'W / be'
        }
    else:
        return {'error': 'Pemadat (b) perlu disesuaikan dengan lebar area pekerjaan (W) agar nilai N menjadi 1'}

# hitung_roller digunakan untuk sheepsfoot roller, pneumatic tire roller, vibratory roller 
def hitung_roller(kondisi_operasi, pemeliharaan_mesin, v, t, b, bo, n, W):
    # Konversi semua input yang relevan ke float
    v = float(v)
    t = float(t)
    b = float(b)
    bo = float(bo)
    n = float(n)
    W = float(W)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat (Fa) untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Menghitung lebar efektif dan jumlah lajur lintasan
    be = b - bo
    N = W / be
    print(f"Debug: Lebar Efektif Pemadatan (be) adalah {be}")
    print(f"Debug: Jumlah Lajur Lintasan (N) adalah {N}")
    
    # Menghitung kapasitas produksi dan koefisien alat
    kapasitas_produksi = (N * be + bo) * v * 1000 * faktor_efisiensi_alat * t / (N * n)
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Kapasitas Produksi (Q) adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")

    if N > b:
        return {
            'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
            'Lebar Efektif Pemadatan, be (m)': be,
            'Jumlah Lajur Lintasan, N': N,
            'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
            'Koefisien Alat (jam)': koefisien_alat,
            'Formula Kapasitas Produksi': '(N * be + bo) * v * 1000 * Faktor Efisiensi Alat * t / (N * n)',
            'Formula Lebar Efektif Pemadatan (be)': 'b - bo',
            'Formula Jumlah Lajur Lintasan (N)': 'W / be'
        }
    else:
        return {'error': 'Pemadat (b) perlu disesuaikan dengan lebar area pekerjaan (W) agar nilai N menjadi 1'}

# hitung_concrete_vibrator digunakan untuk concrete_vibrator, water_pump, jack hammer, blending equipment, asphalt liquid mixer
def hitung_concrete_vibrator(kondisi_operasi, pemeliharaan_mesin, kapasitas_alat):
    # Konversi kapasitas_alat ke float
    kapasitas_alat = float(kapasitas_alat)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Menghitung kapasitas produksi dan koefisien alat
    kapasitas_produksi = kapasitas_alat * faktor_efisiensi_alat
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Kapasitas Produksi adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")

    return {
        'Kapasitas Alat, Ka (m3/jam)': kapasitas_alat,
        'Faktor Efisiensi Alat': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'Formula Kapasitas Produksi': 'Kapasitas Alat * Faktor Efisiensi Alat',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }
#def hitung_water_tank_truck

def hitung_pedestrian_roller(kondisi_operasi, pemeliharaan_mesin, v, t, b, bo, n):
    # Konversi variabel ke float
    v = float(v)
    b = float(b)
    bo = float(bo)
    n = float(n)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Menghitung lebar efektif pemadatan
    be = b - bo
    print(f"Debug: Lebar Efektif Pemadatan (be) adalah {be}")

    # Menghitung kapasitas produksi dan koefisien alat
    kapasitas_produksi = be * v * 1000 * faktor_efisiensi_alat * t / n
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Kapasitas Produksi adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Lebar Efektif Pemadatan, be (m)': be,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'V (m3)': v,
        'Lebar Pemadatan (b)': b,
        'Lebar Area Bebas (bo)': bo,
        'Jumlah Lajur (n)': n,
        'Formula Kapasitas Produksi': 'be * v * 1000 * Faktor Efisiensi Alat * t / n',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }

# hitung_tamper juga digunakan untuk vibrating rammer
def hitung_tamper(kondisi_operasi, pemeliharaan_mesin, v, lbr, t, N, n):
    # Konversi variabel ke float
    v = float(v)
    lbr = float(lbr)
    t = float(t)
    N = float(N)
    n = float(n)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Menghitung kapasitas produksi dan koefisien alat
    kapasitas_produksi = v * 1000 * faktor_efisiensi_alat * lbr * t / (N * n)
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Kapasitas Produksi adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'V (m3)': v,
        'Lebar (lbr)': lbr,
        'Waktu (t)': t,
        'Jumlah Lajur (N)': N,
        'Jumlah Lintasan (n)': n,
        'Formula Kapasitas Produksi': 'v * 1000 * Faktor Efisiensi Alat * lbr * t / (N * n)',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }

def hitung_pulvi_mixer(kondisi_operasi, pemeliharaan_mesin, v, b, t):
    # Konversi variabel ke float
    v = float(v)
    b = float(b)
    t = float(t)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Menghitung kapasitas produksi dan koefisien alat
    kapasitas_produksi = v * 1000 * faktor_efisiensi_alat * b * t
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Kapasitas Produksi adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'V (m3)': v,
        'Lebar (b)': b,
        'Waktu (t)': t,
        'Formula Kapasitas Produksi': 'v * 1000 * Faktor Efisiensi Alat * b * t',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }

def hitung_concrete_pump():
    return{'data sesuai dengan spesifikasi'}

def hitung_pile_driver_hammer(kondisi_operasi, pemeliharaan_mesin, V, p, T1, T2, T3):
    # Konversi variabel ke float
    V = float(V)
    p = float(p)
    T1 = float(T1)
    T2 = float(T2)
    T3 = float(T3)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Menghitung waktu siklus dan kapasitas produksi
    waktu_siklus = T1 + T2 + T3
    kapasitas_produksi = V * p * faktor_efisiensi_alat * 60 / waktu_siklus
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Waktu Siklus adalah {waktu_siklus}")
    print(f"Debug: Kapasitas Produksi adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'V (m3)': V,
        'p (kg/m3)': p,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Formula Kapasitas Produksi': 'V * p * Faktor Efisiensi Alat * 60 / Waktu Siklus',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }

def hitung_welding_set(kondisi_operasi, pemeliharaan_mesin, jarak_antar_sambungan, T):
    # Konversi variabel ke float
    jarak_antar_sambungan = float(jarak_antar_sambungan)
    T = float(T)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Menghitung kapasitas produksi
    kapasitas_produksi = jarak_antar_sambungan * faktor_efisiensi_alat * 60 / T
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Kapasitas Produksi adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (m/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'Jarak Antar Sambungan (m)': jarak_antar_sambungan,
        'Waktu (menit)': T,
        'Formula Kapasitas Produksi': 'Jarak Antar Sambungan * Faktor Efisiensi Alat * 60 / Waktu',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }

def hitung_bored_pile_drilling(kondisi_operasi, pemeliharaan_mesin, V, p, T1, T2, T3, T4, T5, T6, T7, T8, T9):
    # Konversi variabel ke float
    V = float(V)
    p = float(p)
    T1 = float(T1)
    T2 = float(T2)
    T3 = float(T3)
    T4 = float(T4)
    T5 = float(T5)
    T6 = float(T6)
    T7 = float(T7)
    T8 = float(T8)
    T9 = float(T9)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Menghitung waktu siklus dan kapasitas produksi
    waktu_siklus = T1 + T2 + T3 + T4 + T5 + T6 + T7 + T8 + T9
    kapasitas_produksi = V * p * faktor_efisiensi_alat * 60 / waktu_siklus
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Waktu Siklus adalah {waktu_siklus}")
    print(f"Debug: Kapasitas Produksi adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (m/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'V (m3)': V,
        'p (kg/m3)': p,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Formula Kapasitas Produksi': 'V * p * Faktor Efisiensi Alat * 60 / Waktu Siklus',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }


def hitung_road_milling(kondisi_operasi, pemeliharaan_mesin, v, b, t):
    # Konversi variabel ke float
    v = float(v)
    b = float(b)
    t = float(t)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Menghitung kapasitas produksi
    kapasitas_produksi = v * b * t * faktor_efisiensi_alat * 60
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Kapasitas Produksi adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'Volume (m3)': v,
        'Lebar (m)': b,
        'Waktu (menit)': t,
        'Formula Kapasitas Produksi': 'v * b * t * Faktor Efisiensi Alat * 60',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }

def hitung_rock_drill_breaker(kondisi_operasi, pemeliharaan_mesin, V, D, Faktor_breaker, T1, T2):
    # Konversi variabel ke float
    V = float(V)
    D = float(D)
    Faktor_breaker = float(Faktor_breaker)  # Menambahkan konversi untuk Faktor_breaker
    T1 = float(T1)
    T2 = float(T2)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Set nilai Faktor_breaker
    Faktor_breaker = 1
    print(f"Debug: Faktor Breaker di-set ke {Faktor_breaker}")
    
    # Menghitung waktu siklus dan kapasitas produksi
    waktu_siklus = T1 + T2
    kapasitas_produksi = V * D * Faktor_breaker * faktor_efisiensi_alat * 60 / waktu_siklus
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Waktu Siklus adalah {waktu_siklus}")
    print(f"Debug: Kapasitas Produksi adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'Volume (m3)': V,
        'Diameter (m)': D,
        'Faktor Breaker': Faktor_breaker,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Formula Kapasitas Produksi': 'V * D * Faktor Breaker * Faktor Efisiensi Alat * 60 / Waktu Siklus',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }

#hitung recycler digunakan untuk menghitung cold recycler dan hot recycler
def hitung_recycler(kondisi_operasi, pemeliharaan_mesin, v, b, t, satuan):
    # Konversi variabel ke float
    v = float(v)
    b = float(b)
    t = float(t)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")

    if satuan == 'm3/jam':
        # Menghitung kapasitas produksi dalam m3/jam
        kapasitas_produksi = v * b * t * faktor_efisiensi_alat * 60
        koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
        print(f"Debug: Kapasitas Produksi (m3/jam) adalah {kapasitas_produksi}")
        print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")

        return {
            'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
            'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
            'Koefisien Alat (jam)': koefisien_alat,
            'Volume (m3)': v,
            'Lebar (m)': b,
            'Waktu (menit)': t,
            'Formula Kapasitas Produksi': 'v * b * t * Faktor Efisiensi Alat * 60',
            'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
        }
    
    elif satuan == 'm2/jam':
        # Menghitung kapasitas produksi dalam m2/jam
        kapasitas_produksi = v * b * faktor_efisiensi_alat * 60
        koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
        print(f"Debug: Kapasitas Produksi (m2/jam) adalah {kapasitas_produksi}")
        print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")

        return {
            'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
            'Kapasitas Produksi, Q (m2/jam)': kapasitas_produksi,
            'Koefisien Alat (jam)': koefisien_alat,
            'Volume (m3)': v,
            'Lebar (m)': b,
            'Waktu (menit)': t,
            'Formula Kapasitas Produksi': 'v * b * Faktor Efisiensi Alat * 60',
            'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
        }
    
    return 0

def hitung_aggregate_spreader(kondisi_operasi, pemeliharaan_mesin, Cp, b, t, v):
    # Konversi variabel ke float
    Cp = float(Cp)
    b = float(b)
    t = float(t)
    v = float(v)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Menghitung kapasitas produksi
    kapasitas_produksi = Cp * b * t * v * faktor_efisiensi_alat * 1000 / 100
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Kapasitas Produksi (m3/jam) adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")
    
    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'Cp': Cp,
        'Lebar (m)': b,
        'Waktu (menit)': t,
        'Kecepatan (m/menit)': v,
        'Formula Kapasitas Produksi': 'Cp * b * t * v * Faktor Efisiensi Alat * 1000 / 100',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }

def hitung_asphalt_distributor(kondisi_operasi, pemeliharaan_mesin, Cp):
    # Konversi variabel ke float
    Cp = float(Cp)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Menghitung kapasitas produksi
    kapasitas_produksi = Cp * faktor_efisiensi_alat * 60
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Kapasitas Produksi (m3/jam) adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")
    
    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'Cp': Cp,
        'Formula Kapasitas Produksi': 'Cp * Faktor Efisiensi Alat * 60',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }

def hitung_concrete_paving_machine(kondisi_operasi, pemeliharaan_mesin, b, v):
    # Konversi variabel ke float
    b = float(b)
    v = float(v)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Menghitung kapasitas produksi
    kapasitas_produksi = b * v * faktor_efisiensi_alat * 60
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Kapasitas Produksi (m2/jam) adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")
    
    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (m2/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'Lebar (m)': b,
        'Kecepatan (m/menit)': v,
        'Formula Kapasitas Produksi': 'b * v * Faktor Efisiensi Alat * 60',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }

def hitung_batching_plant(kondisi_operasi, pemeliharaan_mesin, V, T1, T2, T3, T4):
    # Konversi variabel ke float
    V = float(V)
    T1 = float(T1)
    T2 = float(T2)
    T3 = float(T3)
    T4 = float(T4)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Menghitung waktu siklus dan kapasitas produksi
    waktu_siklus = T1 + T2 + T3 + T4
    kapasitas_produksi = V * faktor_efisiensi_alat * 60 / (1000 * waktu_siklus)
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Waktu Siklus (menit) adalah {waktu_siklus}")
    print(f"Debug: Kapasitas Produksi (m3/jam) adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")
    
    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'V': V,
        'Waktu Siklus (menit)': waktu_siklus,
        'Formula Kapasitas Produksi': 'V * Faktor Efisiensi Alat * 60 / (1000 * Waktu Siklus)',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }

def hitung_asphalt_tank_truck(kondisi_operasi, pemeliharaan_mesin, Pa):
    # Konversi variabel ke float
    Pa = float(Pa)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Menghitung kapasitas produksi
    kapasitas_produksi = Pa * faktor_efisiensi_alat * 60
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Kapasitas Produksi (m3/jam) adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")
    
    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'Pa': Pa,
        'Formula Kapasitas Produksi': 'Pa * Faktor Efisiensi Alat * 60',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }

def hitung_cement_tank_truck(kondisi_operasi, pemeliharaan_mesin, V, T1, T2, T3, T4):
    # Konversi variabel ke float
    V = float(V)
    T1 = float(T1)
    T2 = float(T2)
    T3 = float(T3)
    T4 = float(T4)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Menghitung waktu siklus dan kapasitas produksi
    waktu_siklus = T1 + T2 + T3 + T4
    kapasitas_produksi = V * faktor_efisiensi_alat * 60 / (1000 * waktu_siklus)
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    print(f"Debug: Waktu Siklus (menit) adalah {waktu_siklus}")
    print(f"Debug: Kapasitas Produksi (m3/jam) adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")
    
    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'V': V,
        'Waktu Siklus (menit)': waktu_siklus,
        'Formula Kapasitas Produksi': 'V * Faktor Efisiensi Alat * 60 / (1000 * Waktu Siklus)',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }

def hitung_concrete_truck_mixer(kondisi_operasi, pemeliharaan_mesin, V, Q1, L, vF, vR, T4, T5):
    # Konversi variabel ke float
    V = float(V)
    Q1 = float(Q1)
    L = float(L)
    vF = float(vF)
    vR = float(vR)
    T4 = float(T4)
    T5 = float(T5)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Menghitung waktu pengisian, waktu tempuh bermuatan, dan waktu tempuh kosong
    waktu_pengisian = V / Q1
    waktu_tempuh_isi = L * 60 / vF
    waktu_tempuh_kosong = L * 60 / vR
    waktu_siklus = waktu_tempuh_isi + waktu_tempuh_kosong + waktu_pengisian + T4 + T5
    
    # Menghitung kapasitas produksi dan koefisien alat
    kapasitas_produksi = V * faktor_efisiensi_alat * 60 / waktu_siklus
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    print(f"Debug: Waktu Pengisian (menit) adalah {waktu_pengisian}")
    print(f"Debug: Waktu Tempuh Bermuatan (menit) adalah {waktu_tempuh_isi}")
    print(f"Debug: Waktu Tempuh Kosong (menit) adalah {waktu_tempuh_kosong}")
    print(f"Debug: Waktu Siklus (menit) adalah {waktu_siklus}")
    print(f"Debug: Kapasitas Produksi (m3/jam) adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")
    
    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Waktu Pengisian, T1 (menit)': waktu_pengisian,
        'Waktu Tempuh Bermuatan, T2 (menit)': waktu_tempuh_isi,
        'Waktu Tempuh Kosong, T3 (menit)': waktu_tempuh_kosong,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'V': V,
        'Q1': Q1,
        'L': L,
        'vF': vF,
        'vR': vR,
        'T4': T4,
        'T5': T5,
        'Formula Kapasitas Produksi': 'V * Faktor Efisiensi Alat * 60 / Waktu Siklus',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }

def hitung_chainsaw(kondisi_operasi, pemeliharaan_mesin, banyak_pohon, jam_kerja):
    # Konversi variabel ke float
    banyak_pohon = float(banyak_pohon)
    jam_kerja = float(jam_kerja)
    
    # Mendapatkan faktor efisiensi alat
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    print(f"Debug: Faktor Efisiensi Alat untuk kondisi operasi {kondisi_operasi} dan pemeliharaan mesin {pemeliharaan_mesin} adalah {faktor_efisiensi_alat}")
    
    # Validasi data input
    if faktor_efisiensi_alat <= 0 or jam_kerja <= 0:
        return {'error': 'Data input tidak valid untuk perhitungan chainsaw'}
    
    # Menghitung kapasitas produksi dan koefisien alat
    kapasitas_produksi = (banyak_pohon * faktor_efisiensi_alat) / jam_kerja
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    print(f"Debug: Kapasitas Produksi (buah/jam) adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")
    
    return {
        'Faktor Efisiensi Alat': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (buah/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'Banyak Pohon': banyak_pohon,
        'Jam Kerja': jam_kerja,
        'Formula Kapasitas Produksi': '(Banyak Pohon * Faktor Efisiensi Alat) / Jam Kerja',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }

def hitung_aplikator_cat_thermoplastic(V, Bc):
    # Convert inputs to float for accurate calculations
    V = float(V)
    Bc = float(Bc)
    
    # Calculate production capacity
    kapasitas_produksi = V / Bc
    # Calculate equipment coefficient
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging statements
    print(f"Debug: Kapasitas Produksi (m2/jam) adalah {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat (jam) adalah {koefisien_alat}")
    
    return {
        'Kapasitas Produksi, Q (m2/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'V': V,
        'Bc': Bc,
        'Formula Kapasitas Produksi': 'V / Bc',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }


# concrete breaker ke drop hammer
def hitung_concrete_breaker(kondisi_operasi, pemeliharaan_mesin, v, b, t):
    # Get the efficiency factor for the equipment
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    
    # Calculate the production capacity
    kapasitas_produksi = b * v * t * faktor_efisiensi_alat * 60
    
    # Calculate the equipment coefficient
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat = {koefisien_alat}")
    
    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'v': v,
        'b': b,
        't': t,
        'Formula Kapasitas Produksi': 'b * v * t * faktor_efisiensi_alat * 60',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }

def hitung_kapal_tongkang(kondisi_operasi, pemeliharaan_mesin, Cp, BiL, Q1, L, vF, vR, T4):
    # Get the efficiency factor for the equipment
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    
    # Calculate time for loading and unloading
    waktu_tempuh_isi = L * 60 / vF
    waktu_tempuh_kosong = L * 60 / vR
    waktu_muat_bongkar = 2 * (Cp * BiL) / Q1
    waktu_siklus = waktu_tempuh_isi + waktu_tempuh_kosong + waktu_muat_bongkar + T4
    
    # Calculate the production capacity
    kapasitas_produksi = Cp * faktor_efisiensi_alat * 60 / waktu_siklus
    
    # Calculate the equipment coefficient
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")
    print(f"Debug: Waktu Tempuh Isi = {waktu_tempuh_isi}")
    print(f"Debug: Waktu Tempuh Kosong = {waktu_tempuh_kosong}")
    print(f"Debug: Waktu Muat Bongkar = {waktu_muat_bongkar}")
    print(f"Debug: Waktu Siklus = {waktu_siklus}")
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat = {koefisien_alat}")
    
    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (ton/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'Cp': Cp,
        'BiL': BiL,
        'Q1': Q1,
        'L': L,
        'vF': vF,
        'vR': vR,
        'T4': T4,
        'Formula Kapasitas Produksi': 'Cp * faktor_efisiensi_alat * 60 / waktu_siklus',
        'Formula Koefisien Alat': '1 / Kapasitas Produksi' if kapasitas_produksi else '0'
    }

def hitung_fork_lift(kondisi_operasi, pemeliharaan_mesin, V, L, vF, vR, T3, T4):
    # Convert inputs to float
    V = float(V)
    L = float(L)
    vF = float(vF)
    vR = float(vR)
    T3 = float(T3)
    T4 = float(T4)

    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    
    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")
    
    waktu_tempuh_isi = L * 60 / vF
    waktu_tempuh_kosong = L * 60 / vR
    waktu_siklus = waktu_tempuh_isi + waktu_tempuh_kosong + T3 + T4
    
    # Debugging statements
    print(f"Debug: Waktu Tempuh Isi = {waktu_tempuh_isi}")
    print(f"Debug: Waktu Tempuh Kosong = {waktu_tempuh_kosong}")
    print(f"Debug: Waktu Siklus = {waktu_siklus}")
    
    kapasitas_produksi = V * faktor_efisiensi_alat * 60 / waktu_siklus
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging statements
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat = {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (ton/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat
    }

def hitung_concrete_cutter(kondisi_operasi, pemeliharaan_mesin, kapasitas_alat):
    # Convert input to float
    kapasitas_alat = float(kapasitas_alat)
    
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    
    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")
    
    kapasitas_produksi = kapasitas_alat * faktor_efisiensi_alat
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging statements
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat = {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (m/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat
    }


def hitung_power_broom(kondisi_operasi, pemeliharaan_mesin, v, b, Kdr):
    # Convert inputs to float
    v = float(v)
    b = float(b)
    Kdr = float(Kdr)
    
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    
    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")

    kapasitas_produksi = v * b * Kdr * faktor_efisiensi_alat * 1000
    
    # Debugging statements
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")

    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging statements
    print(f"Debug: Koefisien Alat = {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat': faktor_efisiensi_alat,
        'Volume, v (m3)': v,
        'Lebar, b (m)': b,
        'Koefisien Daya Residu, Kdr': Kdr,
        'Kapasitas Produksi, Q (liter/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat
    }

def hitung_asphalt_slurry_seal_truck(kondisi_operasi, pemeliharaan_mesin, Cp, v, b):
    # Convert inputs to float
    Cp = float(Cp)
    v = float(v)
    b = float(b)
    
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    
    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")

    kapasitas_produksi = v * b * Cp * faktor_efisiensi_alat * 1000
    
    # Debugging statements
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")

    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging statements
    print(f"Debug: Koefisien Alat = {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (m2/jam)': kapasitas_produksi,
        'Volume, v (m3)': v,
        'Lebar, b (m)': b,
        'Kapasitas Pengguna, Cp': Cp,
        'Koefisien Alat (jam)': koefisien_alat
    }

def hitung_truck_mixer_agitator(kondisi_operasi, pemeliharaan_mesin, V, L, vF, vR, T3, T4):
    # Convert inputs to float
    V = float(V)
    L = float(L)
    vF = float(vF)
    vR = float(vR)
    T3 = float(T3)
    T4 = float(T4)
    
    # Calculate factor of equipment efficiency
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    
    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")

    # Calculate times
    waktu_tempuh_isi = L * 60 / vF
    waktu_tempuh_kosong = L * 60 / vR
    waktu_siklus = waktu_tempuh_isi + waktu_tempuh_kosong + T3 + T4
    
    # Debugging statements
    print(f"Debug: Waktu Tempuh Bermuatan = {waktu_tempuh_isi}")
    print(f"Debug: Waktu Tempuh Kosong = {waktu_tempuh_kosong}")
    print(f"Debug: Waktu Siklus = {waktu_siklus}")

    # Calculate production capacity
    kapasitas_produksi = V * faktor_efisiensi_alat * 60 / waktu_siklus
    
    # Debugging statements
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")

    # Calculate equipment coefficient
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging statements
    print(f"Debug: Koefisien Alat = {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Volume, V (m3)': V,
        'Jarak, L (m)': L,
        'Kecepatan Tempuh Bermuatan, vF (m/jam)': vF,
        'Kecepatan Tempuh Kosong, vR (m/jam)': vR,
        'Waktu Tempuh Bermuatan, T1 (menit)': waktu_tempuh_isi,
        'Waktu Tempuh Kosong, T2 (menit)': waktu_tempuh_kosong,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat
    }

def hitung_self_propelled_mixer(kondisi_operasi, pemeliharaan_mesin, v, b, n, t):
    # Convert inputs to float
    v = float(v)
    b = float(b)
    n = float(n)
    t = float(t)
    
    # Calculate factor of equipment efficiency
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    
    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")

    # Calculate production capacity
    kapasitas_produksi = v * b * t * faktor_efisiensi_alat * 1000 / n
    
    # Debugging statements
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")

    # Calculate equipment coefficient
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging statements
    print(f"Debug: Koefisien Alat = {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Volume, v (m3)': v,
        'Lebar, b (m)': b,
        'Jumlah, n': n,
        'Waktu, t (jam)': t,
        'Kapasitas Produksi, Q (m2/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat
    }

# hitung_stressing_jack juga dapat digunakan untuk grouting pump
def hitung_stressing_jack(kondisi_operasi, pemeliharaan_mesin, V, N, T1, T2):
    # Convert inputs to float
    V = float(V)
    N = float(N)
    T1 = float(T1)
    T2 = float(T2)
    
    # Calculate factor of equipment efficiency
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    
    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")

    # Calculate cycle time and production capacity
    waktu_siklus = T1 + T2
    kapasitas_produksi = V * N * faktor_efisiensi_alat * 60 / waktu_siklus
    
    # Debugging statements
    print(f"Debug: Waktu Siklus = {waktu_siklus}")
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")

    # Calculate equipment coefficient
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging statements
    print(f"Debug: Koefisien Alat = {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Volume, V (m3)': V,
        'Jumlah, N': N,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Kapasitas Produksi, Q (tendon/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat
    }

def hitung_trailer_tronton_30t(kondisi_operasi, pemeliharaan_mesin, V, L, vF, vR, T1, T4, T5):
    # Convert inputs to float
    V = float(V)
    L = float(L)
    vF = float(vF)
    vR = float(vR)
    T1 = float(T1)
    T4 = float(T4)
    T5 = float(T5)
    
    # Calculate factor of equipment efficiency
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    
    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")

    # Calculate times and production capacity
    waktu_tempuh_isi = L * 60 / vF
    waktu_tempuh_kosong = L * 60 / vR
    waktu_siklus = waktu_tempuh_isi + waktu_tempuh_kosong + T1 + T4 + T5
    kapasitas_produksi = V * faktor_efisiensi_alat * 60 / waktu_siklus
    
    # Debugging statements
    print(f"Debug: Waktu Tempuh Bermuatan = {waktu_tempuh_isi}")
    print(f"Debug: Waktu Tempuh Kosong = {waktu_tempuh_kosong}")
    print(f"Debug: Waktu Siklus = {waktu_siklus}")
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")

    # Calculate equipment coefficient
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging statements
    print(f"Debug: Koefisien Alat = {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Volume, V (m3)': V,
        'Jarak, L (m)': L,
        'Kecepatan Bermuatan, vF (m/menit)': vF,
        'Kecepatan Kosong, vR (m/menit)': vR,
        'Waktu Muat, T1 (menit)': T1,
        'Waktu Kosong, T4 (menit)': T4,
        'Waktu Tambahan, T5 (menit)': T5,
        'Waktu Tempuh Bermuatan, T2 (menit)': waktu_tempuh_isi,
        'Waktu Tempuh Kosong, T3 (menit)': waktu_tempuh_kosong,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat
    }

def hitung_ponton(V, Qa, Q1, L, vF, vR, T1, T5):
    # Convert inputs to float
    V = float(V)
    Qa = float(Qa)
    Q1 = float(Q1)
    L = float(L)
    vF = float(vF)
    vR = float(vR)
    T1 = float(T1)
    T5 = float(T5)
    
    # Calculate times
    waktu_tempuh_isi = L * 60 / vF
    waktu_tempuh_kosong = L * 60 / vR
    waktu_tungu_pancang = V * 60 / Q1
    waktu_siklus = waktu_tempuh_isi + waktu_tempuh_kosong + T1 + waktu_tungu_pancang + T5
    
    # Debugging statements
    print(f"Debug: Waktu Tempuh Bermuatan = {waktu_tempuh_isi}")
    print(f"Debug: Waktu Tempuh Kosong = {waktu_tempuh_kosong}")
    print(f"Debug: Waktu Tunggu Pancang = {waktu_tungu_pancang}")
    print(f"Debug: Waktu Siklus = {waktu_siklus}")

    # Calculate production capacity and equipment coefficient
    kapasitas_produksi = V * 60 / waktu_siklus
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging statements
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat = {koefisien_alat}")

    return {
        'Volume, V (m3)': V,
        'Kapasitas Angkut, Qa (m3)': Qa,
        'Kapasitas Pancang, Q1 (m3)': Q1,
        'Jarak, L (m)': L,
        'Kecepatan Bermuatan, vF (m/menit)': vF,
        'Kecepatan Kosong, vR (m/menit)': vR,
        'Waktu Muat, T1 (menit)': T1,
        'Waktu Tambahan, T5 (menit)': T5,
        'Waktu Tempuh Bermuatan, T2 (menit)': waktu_tempuh_isi,
        'Waktu Tempuh Kosong, T4 (menit)': waktu_tempuh_kosong,
        'Waktu Tunggu Pancang (menit)': waktu_tungu_pancang,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat
    }

# hitung boiler dapat juga digunakan untuk Hot Compressor Air Lance (HCA)
def hitung_boiler(kondisi_operasi, pemeliharaan_mesin, V, waktu_siklus):
    # Convert inputs to float
    V = float(V)
    waktu_siklus = float(waktu_siklus)
    
    # Calculate efficiency factor and production capacity
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    kapasitas_produksi = V * faktor_efisiensi_alat * 60 / waktu_siklus
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0

    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")
    print(f"Debug: Waktu Siklus = {waktu_siklus}")
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat = {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Kapasitas Produksi, Q (kg/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'V': V,
        'Waktu Siklus': waktu_siklus,
        'Formula Kapasitas Produksi': 'V * Fa * 60 / Ts',
        'Formula Koefisien Alat': '1 / Q'
    }

def hitung_drum_mixer(kondisi_operasi, pemeliharaan_mesin, V, T1, T2, T3):
    # Convert inputs to float
    V = float(V)
    T1 = float(T1)
    T2 = float(T2)
    T3 = float(T3)
    
    # Calculate efficiency factor and production capacity
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    waktu_siklus = T1 + T2 + T3
    kapasitas_produksi = V * faktor_efisiensi_alat * 60 / waktu_siklus
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0

    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")
    print(f"Debug: Waktu Siklus = {waktu_siklus}")
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat = {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Kapasitas Produksi, Q (kg/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'V': V,
        'T1': T1,
        'T2': T2,
        'T3': T3,
        'Formula Kapasitas Produksi': 'V * Fa * 60 / Ts',
        'Formula Koefisien Alat': '1 / Q'
    }

def hitung_silicon_seal_pump(kondisi_operasi, pemeliharaan_mesin, V, Ws):
    # Convert inputs to float
    V = float(V)
    Ws = float(Ws)
    
    # Calculate efficiency factor and production capacity
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    kapasitas_produksi = V * faktor_efisiensi_alat / Ws
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0

    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat = {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (1/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'V': V,
        'Ws': Ws,
        'Formula Kapasitas Produksi': 'V * Fa / Ws',
        'Formula Koefisien Alat': '1 / Q'
    }

def hitung_kunci_torsi(kondisi_operasi, pemeliharaan_mesin, T1, T2, T3, T4):
    # Convert inputs to float
    T1 = float(T1)
    T2 = float(T2)
    T3 = float(T3)
    T4 = float(T4)
    
    # Calculate efficiency factor and production capacity
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    waktu_siklus = T1 + T2 + T3 + T4
    kapasitas_produksi = faktor_efisiensi_alat * 60 / waktu_siklus
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0

    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")
    print(f"Debug: Waktu Siklus = {waktu_siklus}")
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat = {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Kapasitas Produksi, Q (buah/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'T1': T1,
        'T2': T2,
        'T3': T3,
        'T4': T4,
        'Formula Kapasitas Produksi': 'Fa * 60 / Ts',
        'Formula Koefisien Alat': '1 / Q'
    }

# hitung gerinda tangan dapat digunakan untuk Water Jet Blasting, Mesin Amplas Kayu
def hitung_gerinda_tangan(kondisi_operasi, pemeliharaan_mesin, kapasitas_alat):
    # Convert inputs to float
    kapasitas_alat = float(kapasitas_alat)
    
    # Calculate efficiency factor and production capacity
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    kapasitas_produksi = kapasitas_alat * faktor_efisiensi_alat
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat = {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (m2/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'Kapasitas Alat': kapasitas_alat,
        'Formula Kapasitas Produksi': 'Kapasitas Alat * Fa',
        'Formula Koefisien Alat': '1 / Q'
    }

def hitung_hand_mixer(kondisi_operasi, pemeliharaan_mesin, V, T1, T2):
    # Convert inputs to float
    V = float(V)
    T1 = float(T1)
    T2 = float(T2)
    
    # Calculate efficiency factor and production capacity
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    waktu_siklus = T1 + T2
    kapasitas_produksi = V * faktor_efisiensi_alat * 60 / waktu_siklus
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")
    print(f"Debug: Waktu Siklus = {waktu_siklus}")
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat = {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Kapasitas Produksi, Q (kg/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'V': V,
        'T1': T1,
        'T2': T2,
        'Formula Kapasitas Produksi': 'V * Fa * 60 / Ts',
        'Formula Koefisien Alat': '1 / Q'
    }

def hitung_mesin_bor(kondisi_operasi, pemeliharaan_mesin, V, Nb, T1, T2):
    # Convert inputs to float
    V = float(V)
    Nb = float(Nb)
    T1 = float(T1)
    T2 = float(T2)
    
    # Calculate efficiency factor and production capacity
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    waktu_siklus = T1 + T2
    kapasitas_produksi = V * faktor_efisiensi_alat * 60 / (Nb * waktu_siklus)
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")
    print(f"Debug: Waktu Siklus = {waktu_siklus}")
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat = {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'V': V,
        'Nb': Nb,
        'T1': T1,
        'T2': T2,
        'Formula Kapasitas Produksi': 'V * Fa * 60 / (Nb * Ts)',
        'Formula Koefisien Alat': '1 / Q'
    }

def hitung_stamper(kondisi_operasi, pemeliharaan_mesin, bp, L):
    # Convert inputs to float
    bp = float(bp)
    L = float(L)
    
    # Calculate efficiency factor and production capacity
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    kapasitas_produksi = bp * faktor_efisiensi_alat / L
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat = {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kapasitas Produksi, Q (m3/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'BP': bp,
        'L': L,
        'Formula Kapasitas Produksi': 'BP * Fa / L',
        'Formula Koefisien Alat': '1 / Q'
    }

def hitung_lift_barang(alat, kondisi_operasi, pemeliharaan_mesin, Cp, H, T1, T3):
    # Convert inputs to float
    Cp = float(Cp)
    H = float(H)
    T1 = float(T1)
    T3 = float(T3)
    
    # Determine lift speed based on equipment type
    if alat == "Lift Barang, Tinggi 6-10 lantai (20-40 m), Bm 1,0 ton":
        kecepatan_lift = 10
    elif alat == "Lift Barang, Tinggi 10-24 lantai (40-100 m), Bm 1,0 ton":
        kecepatan_lift = 20
    else:
        kecepatan_lift = 30
    
    # Calculate efficiency factor, cycle time, and production capacity
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    waktu_tempuh_lift = H / kecepatan_lift
    waktu_siklus = T1 + waktu_tempuh_lift + T3
    kapasitas_produksi = Cp * faktor_efisiensi_alat * 60 / waktu_siklus
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")
    print(f"Debug: Kecepatan Lift = {kecepatan_lift}")
    print(f"Debug: Waktu Tempuh Lift = {waktu_tempuh_lift}")
    print(f"Debug: Waktu Siklus = {waktu_siklus}")
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat = {koefisien_alat}")

    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Kecepatan Lift, v (m/menit)': kecepatan_lift,
        'Waktu Tempuh Lift, T2 (menit)': waktu_tempuh_lift,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Kapasitas Produksi, Q (ton/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'Cp': Cp,
        'H': H,
        'T1': T1,
        'T3': T3,
        'Formula Kapasitas Produksi': 'Cp * Fa * 60 / Ts',
        'Formula Koefisien Alat': '1 / Q'
    }

def hitung_lokasi_crane(alat, kondisi_operasi, pemeliharaan_mesin, V, lokasi):
    # Convert inputs to float
    V = float(V)
    print(f"V = {V}")
    print(f"alat = {alat}")
    print(f"Lokasi = {lokasi}")
    # Calculate efficiency factor and cycle time
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    waktu_siklus = float(get_waktu_siklus_crane_lokasi(alat, lokasi))
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")
    print(f"Debug: Waktu Siklus = {waktu_siklus}")

    kapasitas_produksi = V * faktor_efisiensi_alat * 60 / waktu_siklus
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging statements
    
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat = {koefisien_alat}")
    
    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Kapasitas Produksi, Q (ton/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'V': V,
        'Lokasi': lokasi,
        'Formula Kapasitas Produksi': 'V * Fa * 60 / Ts',
        'Formula Koefisien Alat': '1 / Q'
    }

def hitung_lantai_crane(alat, kondisi_operasi, pemeliharaan_mesin, V, lantai):
    # Convert inputs to float
    V = float(V)
    
    # Calculate efficiency factor and cycle time
    faktor_efisiensi_alat = get_faktor_efisiensi_alat(kondisi_operasi, pemeliharaan_mesin)
    waktu_siklus = get_waktu_siklus_crane_lantai(alat, lantai)
    kapasitas_produksi = V * faktor_efisiensi_alat * 60 / waktu_siklus
    koefisien_alat = 1 / kapasitas_produksi if kapasitas_produksi else 0
    
    # Debugging statements
    print(f"Debug: Faktor Efisiensi Alat = {faktor_efisiensi_alat}")
    print(f"Debug: Waktu Siklus = {waktu_siklus}")
    print(f"Debug: Kapasitas Produksi = {kapasitas_produksi}")
    print(f"Debug: Koefisien Alat = {koefisien_alat}")
    
    return {
        'Faktor Efisiensi Alat, Fa': faktor_efisiensi_alat,
        'Waktu Siklus, Ts (menit)': waktu_siklus,
        'Kapasitas Produksi, Q (ton/jam)': kapasitas_produksi,
        'Koefisien Alat (jam)': koefisien_alat,
        'V': V,
        'Lantai': lantai,
        'Formula Kapasitas Produksi': 'V * Fa * 60 / Ts',
        'Formula Koefisien Alat': '1 / Q'
    }
    

# Mengambil data input dan memberikan hasil ke index.html
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        alat = request.form.get('alat')
        if alat == 'Asphalt Mixing Plant (AMP)':
            hasil = hitung_amp(
                request.form.get('kondisi_operasi_amp'),
                request.form.get('pemeliharaan_mesin_amp'),
                request.form.get('kapasitas_alat_amp')
            )
        elif alat == 'Asphalt Finisher (Asphalt Paving Machine)':
            hasil = hitung_asphalt_finisher(
                request.form.get('kondisi_operasi_af'),
                request.form.get('pemeliharaan_mesin_af'),
                request.form.get('v_af'),
                request.form.get('b_af'),
                request.form.get('D1_af'),
                request.form.get('t_af'),
                request.form.get('satuan_af')
            )
        elif alat == 'Asphalt Sprayer (Hand Sprayer)':
            hasil = hitung_asphalt_sprayer(
                request.form.get('kondisi_operasi_as'),
                request.form.get('pemeliharaan_mesin_as'),
                request.form.get('Pa_as'),
                request.form.get('lt_as'),
                request.form.get('satuan_as')
            )
        elif alat == 'Bulldozer':
            hasil = hitung_bulldozer(
                request.form.get('kondisi_operasi_bull'),
                request.form.get('kondisi_kerja_bull'),
                request.form.get('b_bull'),
                request.form.get('bo_bull'),
                request.form.get('W_bull'),
                request.form.get('n_bull'),
                request.form.get('H_bull'),
                request.form.get('kemiringan_pisau_bull'),
                request.form.get('vF_bull'), 
                request.form.get('vR_bull'),
                request.form.get('l_bull'),
                request.form.get('jenis_transmisi_bull')
            )
        elif alat == 'Air Compressor':
            hasil=hitung_air_compressor(
                request.form.get('kondisi_operasi_ac'), 
                request.form.get('pemeliharaan_mesin_ac'), 
                request.form.get('penggunaan_ac'), 
                request.form.get('kapasitas_alat_ac')
            )
        elif alat == 'Concrete Mixer':
            hasil=hitung_concrete_mixer(
                request.form.get('kondisi_operasi_cm'), 
                request.form.get('pemeliharaan_mesin_cm'),
                request.form.get('Cp_cm'),
                request.form.get('T1_cm'), 
                request.form.get('T2_cm'), 
                request.form.get('T3_cm'), 
                request.form.get('T4_cm')
            )  
        elif alat == 'Crane (10-15 ton)':
            hasil = hitung_crane_10_15_ton(
                request.form.get('kondisi_operasi_ct'), 
                request.form.get('pemeliharaan_mesin_ct'), 
                request.form.get('V_ct'), 
                request.form.get('T1_ct'), 
                request.form.get('T2_ct')
            )
        elif alat == 'Crane On Track (Crawler Crane) 75 Ton':
            hasil = hitung_crane_10_15_ton(
                request.form.get('kondisi_operasi_cot'), 
                request.form.get('pemeliharaan_mesin_cot'), 
                request.form.get('V_cot'), 
                request.form.get('T1_cot'), 
                request.form.get('T2_cot')
            )
        elif alat == 'Crane On Track 75-100 ton':
            hasil = hitung_crane_10_15_ton(
                request.form.get('kondisi_operasi_cot2'), 
                request.form.get('pemeliharaan_mesin_cot2'), 
                request.form.get('V_cot2'), 
                request.form.get('T1_cot2'), 
                request.form.get('T2_cot2')
            )
        elif alat == 'Dump Truck':
            hasil = hitung_dump_truck(
                request.form.get('kondisi_kerja_dump'), 
                request.form.get('kondisi_lapangan_dump'), 
                request.form.get('V_dump'), 
                request.form.get('BiL_dump'), 
                request.form.get('L_dump'), 
                request.form.get('T1_dump'), 
                request.form.get('T4_dump')
            )
        elif alat == 'Truck Semi Trailer, 15 ton':
            hasil = hitung_dump_truck(
                request.form.get('kondisi_kerja_tst'), 
                request.form.get('kondisi_lapangan_tst'), 
                request.form.get('V_tst'), 
                request.form.get('BiL_tst'), 
                request.form.get('L_tst'), 
                request.form.get('T1_tst'), 
                request.form.get('T4_tst')
            )
        elif alat == 'Excavator':
            hasil = hitung_excavator(
                request.form.get('kondisi_operasi_exc'),
                request.form.get('kondisi_galian'),
                request.form.get('kondisi_dumping'),
                request.form.get('kapasitas_bucket'),
                request.form.get('sudut_putar'),
                request.form.get('kondisi_tanah')
            )
        elif alat == 'Chainsaw':
            hasil = hitung_chainsaw(
                request.form.get('kondisi_operasi'),
                request.form.get('pemeliharaan_mesin'),
                request.form.get('banyak_pohon'),
                request.form.get('jam_kerja')
            )
        elif alat == 'Flatbed Truck':
            hasil = hitung_flat_bed_truck(
                request.form.get('kondisi_operasi_flat'),
                request.form.get('pemeliharaan_mesin_flat'),
                request.form.get('kapasitas_alat'),
                request.form.get('jarak_lokasi'),
                request.form.get('kecepatan_bermuatan'),
                request.form.get('kecepatan_kosong'),
                request.form.get('waktu_muat'),
                request.form.get('waktu_bongkar')
            )
        elif alat == 'Generating Set (Genset)':
            hasil = hitung_generating_set(
                request.form.get('kondisi_operasi_genset'), 
                request.form.get('pemeliharaan_mesin_genset'), 
                request.form.get('V_genset')
            )
        elif alat == 'Motor Grader':
            hasil = hitung_motor_grader(
                request.form.get('kondisi_operasi_motor'), 
                request.form.get('uraian_pekerjaan_motor'), 
                request.form.get('Lh_motor'), 
                request.form.get('sudut_pisau_motor'), 
                request.form.get('b_motor'), 
                request.form.get('bo_motor'),
                request.form.get('n_motor'), 
                request.form.get('W_motor'), 
                request.form.get('T2_motor')
            )
        elif alat == 'Track Loader':
            hasil = hitung_track_loader(
                request.form.get('kondisi_operasi_tloader'), 
                request.form.get('kondisi_penumpahan_tloader'), 
                request.form.get('kondisi_kerja_tloader'), 
                request.form.get('cara_pengisian_tloader'), 
                request.form.get('kapasitas_bucket_tloader'), 
                request.form.get('jarak_pergerakan_tloader'), 
                request.form.get('L_tloader'), 
                request.form.get('Z_tloader')
            )
        elif alat == 'Wheel Loader':
            hasil = hitung_wheel_loader(
                request.form.get('kondisi_operasi_wloader'), 
                request.form.get('kondisi_penumpahan_wloader'), 
                request.form.get('kondisi_kerja_wloader'), 
                request.form.get('cara_pengisian_wloader'), 
                request.form.get('kapasitas_bucket_wloader'), 
                request.form.get('jarak_pergerakan_wloader'), 
                request.form.get('L_wloader'), 
                request.form.get('Z_wloader')
            )
        elif alat == 'Three Wheel Loader (TWR/Macadam Roller)':
            hasil = hitung_TWR(
                request.form.get('kondisi_operasi_twr'), 
                request.form.get('pemeliharaan_mesin_twr'),
                request.form.get('v_twr'), 
                request.form.get('t_twr'), 
                request.form.get('b_twr'), 
                request.form.get('bo_twr'), 
                request.form.get('n_twr'), 
                request.form.get('W_twr')
            )
        elif alat == 'Tandem Roller':
            hasil = hitung_TWR(
                request.form.get('kondisi_operasi_tandem'), 
                request.form.get('pemeliharaan_mesin_tandem'),
                request.form.get('v_tandem'), 
                request.form.get('t_tandem'), 
                request.form.get('b_tandem'), 
                request.form.get('bo_tandem'), 
                request.form.get('n_tandem'), 
                request.form.get('W_tandem')
            )
        elif alat == 'Penumatic Tire Roller':
            hasil = hitung_roller(
                request.form.get('kondisi_operasi_pneumatic'), 
                request.form.get('pemeliharaan_mesin_pneumatic'),
                request.form.get('v_pneumatic'),
                request.form.get('t_pneumatic'),
                request.form.get('b_pneumatic'),
                request.form.get('bo_pneumatic'),
                request.form.get('n_pneumatic'),
                request.form.get('W_pneumatic')
            )
        elif alat == 'Sheepsfoot Roller':
            hasil = hitung_roller(
                request.form.get('kondisi_operasi_sheep'), 
                request.form.get('pemeliharaan_mesin_sheep'),
                request.form.get('v_sheep'),
                request.form.get('t_sheep'),
                request.form.get('b_sheep'),
                request.form.get('bo_sheep'),
                request.form.get('n_sheep'),
                request.form.get('W_sheep')
            )
        elif alat == 'Vibratory Roller':
            hasil = hitung_roller(
                request.form.get('kondisi_operasi_vr'), 
                request.form.get('pemeliharaan_mesin_vr'),
                request.form.get('v_vr'),
                request.form.get('t_vr'),
                request.form.get('b_vr'),
                request.form.get('bo_vr'),
                request.form.get('n_vr'),
                request.form.get('W_vr')
            )
        elif alat == 'Concrete Vibrator':
            hasil = hitung_concrete_vibrator(
                request.form.get('kondisi_operasi_cv'), 
                request.form.get('pemeliharaan_mesin_cv'),
                request.form.get('kapasitas_alat_cv')
            )
        elif alat == 'Water Pump':
            hasil = hitung_concrete_vibrator(
                request.form.get('kondisi_operasi_pump'), 
                request.form.get('pemeliharaan_mesin_pump'),
                request.form.get('kapasitas_alat_pump')
            )
        elif alat == 'Jack Hammer':
            hasil = hitung_concrete_vibrator(
                request.form.get('kondisi_operasi_jack'), 
                request.form.get('pemeliharaan_mesin_jack'),
                request.form.get('kapasitas_alat_jack')
            )
        elif alat == 'Blending Equipment':
            hasil = hitung_concrete_vibrator(
                request.form.get('kondisi_operasi_blend'), 
                request.form.get('pemeliharaan_mesin_blend'),
                request.form.get('kapasitas_alat_blend')
            )
        elif alat == 'Asphalt Liquid Mixer':
            hasil = hitung_concrete_vibrator(
                request.form.get('kondisi_operasi_alm'), 
                request.form.get('pemeliharaan_mesin_alm'),
                request.form.get('kapasitas_alat_alm')
            )
        elif alat == 'Pedestrian Roller':
            hasil = hitung_pedestrian_roller(
                request.form.get('kondisi_operasi_ped'), 
                request.form.get('pemeliharaan_mesin_ped'),
                request.form.get('v_ped'),
                request.form.get('t_ped'),
                request.form.get('b_ped'),
                request.form.get('bo_ped'),
                request.form.get('n_ped')
            )
        elif alat == 'Tamper':
            hasil = hitung_tamper(
                request.form.get('kondisi_operasi_tamper'), 
                request.form.get('pemeliharaan_mesin_tamper'),
                1,
                request.form.get('lbr_tamper'),
                request.form.get('t_tamper'),
                request.form.get('N_tamper'),
                request.form.get('n_tamper')
            )
        elif alat == 'Vibrating Rammer':
            hasil = hitung_tamper(
                request.form.get('kondisi_operasi_vib'), 
                request.form.get('pemeliharaan_mesin_vib'),
                request.form.get('v_vib'),
                request.form.get('lbr_vib'),
                request.form.get('t_vib'),
                request.form.get('N_vib'),
                request.form.get('n_vib')
            )
        elif alat == 'Pulvi Mixer (Soil Stabilizer)':
            hasil = hitung_pulvi_mixer(
                request.form.get('kondisi_operasi_pulvi'), 
                request.form.get('pemeliharaan_mesin_pulvi'),
                request.form.get('v_pulvi'),
                request.form.get('b_pulvi'),
                request.form.get('t_pulvi')
            )
        elif alat == 'Concrete Pump':
            hasil = hitung_concrete_pump()  # Asumsi tidak ada parameter untuk concrete pump
        elif alat == 'Pile Driver-Hammer':
            hasil = hitung_pile_driver_hammer(
                request.form.get('kondisi_operasi_pdh'), 
                request.form.get('pemeliharaan_mesin_pdh'),
                request.form.get('V_pdh'),
                request.form.get('p_pdh'),
                request.form.get('T1_pdh'),
                request.form.get('T2_pdh'),
                request.form.get('T3_pdh')
            )
        elif alat == 'Welding Set':
            hasil = hitung_welding_set(
                request.form.get('kondisi_operasi_weld'), 
                request.form.get('pemeliharaan_mesin_weld'),
                request.form.get('jarak_antar_sambungan_weld'),
                request.form.get('T_weld')
            )
        elif alat == 'Bored Pile Drilling Machine, Max. dia. 2 m':
            hasil = hitung_bored_pile_drilling(
                request.form.get('kondisi_operasi_bored'), 
                request.form.get('pemeliharaan_mesin_bored'),
                request.form.get('V_bored'),
                request.form.get('p_bored'),
                request.form.get('T1_bored'),
                request.form.get('T2_bored'),
                request.form.get('T3_bored'),
                request.form.get('T4_bored'),
                request.form.get('T5_bored'),
                request.form.get('T6_bored'),
                request.form.get('T7_bored'),
                request.form.get('T8_bored'),
                request.form.get('T9_bored')
            )
        elif alat == 'Road Milling Machine':
            hasil = hitung_road_milling(
                request.form.get('kondisi_operasi_mill'), 
                request.form.get('pemeliharaan_mesin_mill'),
                request.form.get('v_mill'),
                request.form.get('b_mill'),
                request.form.get('t_mill')
            )
        elif alat == 'Rock Drill Breaker':
            hasil = hitung_rock_drill_breaker(
                request.form.get('kondisi_operasi_rock'), 
                request.form.get('pemeliharaan_mesin_rock'),
                request.form.get('V_rock'),
                request.form.get('D_rock'),
                request.form.get('Faktor_breaker_rock'),
                request.form.get('T1_rock'),
                request.form.get('T2_rock')
            )
        elif alat == 'Cold Recycler':
            hasil = hitung_recycler(
                request.form.get('kondisi_operasi_cold'), 
                request.form.get('pemeliharaan_mesin_cold'),
                request.form.get('v_cold'),
                request.form.get('b_cold'),
                request.form.get('t_cold'),
                request.form.get('satuan_cold')
            )
        elif alat == 'Hot Recycler':
            hasil = hitung_recycler(
                request.form.get('kondisi_operasi_hot'), 
                request.form.get('pemeliharaan_mesin_hot'),
                request.form.get('v_hot'),
                request.form.get('b_hot'),
                request.form.get('t_hot'),
                request.form.get('satuan_hot')
            )
        elif alat == 'Aggregate Spreader':
            hasil = hitung_aggregate_spreader(
                request.form.get('kondisi_operasi_agg'), 
                request.form.get('pemeliharaan_mesin_agg'),
                request.form.get('Cp_agg'),
                request.form.get('b_agg'),
                request.form.get('t_agg'),
                request.form.get('v_agg')
            )
        elif alat == 'Asphalt Distributor':
            hasil = hitung_asphalt_distributor(
                request.form.get('kondisi_operasi_asd'), 
                request.form.get('pemeliharaan_mesin_asd'),
                request.form.get('Cp_asd')
            )
        elif alat == 'Concrete Paving Machine':
            hasil = hitung_concrete_paving_machine(
                request.form.get('kondisi_operasi_cpm'), 
                request.form.get('pemeliharaan_mesin_cpm'),
                request.form.get('b_cpm'),
                request.form.get('v_cpm')
            )
        elif alat == 'Batching Plant (Concrete Pan Mixer)':
            hasil = hitung_batching_plant(
                request.form.get('kondisi_operasi_batch'), 
                request.form.get('pemeliharaan_mesin_batch'),
                request.form.get('V_batch'),
                request.form.get('T1_batch'),
                request.form.get('T2_batch'),
                request.form.get('T3_batch'),
                request.form.get('T4_batch')
            )
        elif alat == 'Concrete Breaker (Drop Hammer)':
            hasil = hitung_concrete_breaker(
                request.form.get('kondisi_operasi_hammer'), 
                request.form.get('pemeliharaan_mesin_hammer'),
                request.form.get('v_hammer'),
                request.form.get('b_hammer'),
                request.form.get('t_hammer')
            )
        elif alat == 'Asphalt Tank Truck':
            hasil = hitung_asphalt_tank_truck(
                request.form.get('kondisi_operasi_att'), 
                request.form.get('pemeliharaan_mesin_att'),
                request.form.get('Pa_att')
            )
        elif alat == 'Cement Tank Truck':
            hasil = hitung_cement_tank_truck(
                request.form.get('kondisi_operasi_ctt'), 
                request.form.get('pemeliharaan_mesin_ctt'),
                request.form.get('V_ctt'),
                request.form.get('T1_ctt'),
                request.form.get('T2_ctt'),
                request.form.get('T3_ctt'),
                request.form.get('T4_ctt')
            )
        elif alat == 'Concrete Truck Mixer':
            hasil = hitung_concrete_truck_mixer(
                request.form.get('kondisi_operasi_ctm'), 
                request.form.get('pemeliharaan_mesin_ctm'),
                request.form.get('V_ctm'),
                request.form.get('Q1_ctm'),
                request.form.get('L_ctm'),
                request.form.get('vF_ctm'),
                request.form.get('vR_ctm'),
                request.form.get('T4_ctm'),
                request.form.get('T5_ctm')
            )
        elif alat == 'Bore Pile Machine dia. 60 cm':
            hasil = hitung_bored_pile_drilling(
                request.form.get('kondisi_operasi_bor60'), 
                request.form.get('pemeliharaan_mesin_bor60'),
                request.form.get('V_bor60'),
                request.form.get('p_bor60'),
                request.form.get('T1_bor60'),
                request.form.get('T2_bor60'),
                request.form.get('T3_bor60'),
                request.form.get('T4_bor60'),
                request.form.get('T5_bor60'),
                request.form.get('T6_bor60'),
                request.form.get('T7_bor60'),
                request.form.get('T8_bor60'),
                request.form.get('T9_bor60')
            )
        elif alat == 'Aplikator Cat Marka Jalan Thermoplastic':
            hasil = hitung_aplikator_cat_thermoplastic(
                request.form.get('V_cat'),
                request.form.get('Bc_cat')
            )
        elif alat == 'Kapal Tongkang/Perahu':
            hasil = hitung_kapal_tongkang(
                request.form.get('kondisi_operasi_kapal'), 
                request.form.get('pemeliharaan_mesin_kapal'),
                request.form.get('Cp_kapal'),
                request.form.get('BiL_kapal'),
                request.form.get('Q1_kapal'),
                request.form.get('L_kapal'),
                request.form.get('vF_kapal'),
                request.form.get('vR_kapal'),
                request.form.get('T4_kapal')
            )
        elif alat == 'Fork Lift':
            hasil = hitung_fork_lift(
                request.form.get('kondisi_operasi_fork'), 
                request.form.get('pemeliharaan_mesin_fork'),
                request.form.get('V_fork'),
                request.form.get('L_fork'),
                request.form.get('vF_fork'),
                request.form.get('vR_fork'),
                request.form.get('T3_fork'),
                request.form.get('T4_fork')
            )
        elif alat == 'Concrete Cutter':
            hasil = hitung_concrete_cutter(
                request.form.get('kondisi_operasi_cutt'), 
                request.form.get('pemeliharaan_mesin_cutt'),
                request.form.get('kapasitas_alat_cutt')
            )
        elif alat == 'Power Broom':
            hasil = hitung_power_broom(
                request.form.get('kondisi_operasi_broom'), 
                request.form.get('pemeliharaan_mesin_broom'),
                request.form.get('v_broom'),
                request.form.get('b_broom'),
                request.form.get('Kdr_broom')
            )
        elif alat == 'Asphalt Slurry Seal Truck':
            hasil = hitung_asphalt_slurry_seal_truck(
                request.form.get('kondisi_operasi_asst'), 
                request.form.get('pemeliharaan_mesin_asst'),
                request.form.get('Cp_asst'),
                request.form.get('v_asst'),
                request.form.get('b_asst')
            )
        elif alat == 'Truck Mixer Agitator':
            hasil = hitung_truck_mixer_agitator(
                request.form.get('kondisi_operasi_tma'), 
                request.form.get('pemeliharaan_mesin_tma'),
                request.form.get('V_tma'),
                request.form.get('L_tma'),
                request.form.get('vF_tma'),
                request.form.get('vR_tma'),
                request.form.get('T3_tma'),
                request.form.get('T4_tma')
            )
        elif alat == 'Self Propelled Mixer':
            hasil = hitung_self_propelled_mixer(
                request.form.get('kondisi_operasi_spm'), 
                request.form.get('pemeliharaan_mesin_spm'),
                request.form.get('v_spm'),
                request.form.get('b_spm'),
                request.form.get('n_spm'),
                request.form.get('t_spm')
            )
        elif alat == 'Stressing Jack':
            hasil = hitung_stressing_jack(
                request.form.get('kondisi_operasi_stress'), 
                request.form.get('pemeliharaan_mesin_stress'),
                request.form.get('V_stress'),
                request.form.get('N_stress'),
                request.form.get('T1_stress'),
                request.form.get('T2_stress')
            )
        elif alat == 'Grouting Pump':
            hasil = hitung_stressing_jack(
                request.form.get('kondisi_operasi_grout'), 
                request.form.get('pemeliharaan_mesin_grout'),
                request.form.get('V_grout'),
                request.form.get('N_grout'),
                request.form.get('T1_grout'),
                request.form.get('T2_grout')
            )
        elif alat == 'Trailer Tronton 30 T':
            hasil = hitung_trailer_tronton_30t(
                request.form.get('kondisi_operasi_tronton'), 
                request.form.get('pemeliharaan_mesin_tronton'),
                request.form.get('V_tronton'),
                request.form.get('L_tronton'),
                request.form.get('vF_tronton'),
                request.form.get('vR_tronton'),
                request.form.get('T1_tronton'),
                request.form.get('T4_tronton'),
                request.form.get('T5_tronton')
            )
        elif alat == 'Ponton + Tug Boat':
            hasil = hitung_ponton(
                request.form.get('V_ponton'),
                request.form.get('Qa_ponton'),
                request.form.get('Q1_ponton'),
                request.form.get('L_ponton'),
                request.form.get('vF_ponton'),
                request.form.get('vR_ponton'),
                request.form.get('T1_ponton'),
                request.form.get('T5_ponton')
            )
        elif alat == 'Pre Heater/ Boiler':
            hasil = hitung_boiler(
                request.form.get('kondisi_operasi_boil'), 
                request.form.get('pemeliharaan_mesin_boil'),
                request.form.get('V_boil'),
                request.form.get('waktu_siklus_boil')
            )
        elif alat == 'Drum Mixer Khusus':
            hasil = hitung_drum_mixer(
                request.form.get('kondisi_operasi_dmk'), 
                request.form.get('pemeliharaan_mesin_dmk'),
                request.form.get('V_dmk'),
                request.form.get('T1_dmk'),
                request.form.get('T2_dmk'),
                request.form.get('T3_dmk')
            )
        elif alat == 'Hot Compressor Air Lance (HCA)':
            hasil = hitung_boiler(
                request.form.get('kondisi_operasi_hca'), 
                request.form.get('pemeliharaan_mesin_hca'),
                request.form.get('V_hca'),
                request.form.get('waktu_siklus_hca')
            )
        elif alat == 'Silicon Seal Pump':
            hasil = hitung_silicon_seal_pump(
                request.form.get('kondisi_operasi_silicon'), 
                request.form.get('pemeliharaan_mesin_silicon'),
                request.form.get('V_silicon'),
                request.form.get('Ws_silicon')
            )
        elif alat == 'Kunci Torsi (Torque Wrench)':
            hasil = hitung_kunci_torsi(
                request.form.get('kondisi_operasi_torsi'), 
                request.form.get('pemeliharaan_mesin_torsi'),
                request.form.get('T1_torsi'),
                request.form.get('T2_torsi'),
                request.form.get('T3_torsi'),
                request.form.get('T4_torsi')
            )
        elif alat == 'Gerinda Tangan':
            hasil = hitung_gerinda_tangan(
                request.form.get('kondisi_operasi_gerinda'), 
                request.form.get('pemeliharaan_mesin_gerinda'),
                request.form.get('kapasitas_alat_gerinda')
            )
        elif alat == 'Water Jet Blasting':
            hasil = hitung_gerinda_tangan(
                request.form.get('kondisi_operasi_jet'), 
                request.form.get('pemeliharaan_mesin_jet'),
                request.form.get('kapasitas_alat_jet')
            )
        elif alat == 'Hand Mixer':
            hasil = hitung_hand_mixer(
                request.form.get('kondisi_operasi_hand'), 
                request.form.get('pemeliharaan_mesin_hand'),
                request.form.get('V_hand'),
                request.form.get('T1_hand'),
                request.form.get('T2_hand')
            )
        elif alat == 'Mesin Bor':
            hasil = hitung_mesin_bor(
                request.form.get('kondisi_operasi_bor'), 
                request.form.get('pemeliharaan_mesin_bor'),
                request.form.get('V_bor'),
                request.form.get('Nb_bor'),
                request.form.get('T1_bor'),
                request.form.get('T2_bor')
            )
        elif alat == 'Mesin Amplas Kayu':
            hasil = hitung_gerinda_tangan(
                request.form.get('kondisi_operasi_amplas'), 
                request.form.get('pemeliharaan_mesin_amplas'),
                request.form.get('kapasitas_alat_amplas')
            )
        elif alat == 'Stamper':
            hasil = hitung_stamper(
                request.form.get('kondisi_operasi_stamper'), 
                request.form.get('pemeliharaan_mesin_stamper'),
                request.form.get('bp_stamper'),
                request.form.get('L_stamper')
            )
        elif alat == 'Lift Barang, Tinggi 6-10 lantai (20-40 m), Bm 1,0 ton':
            hasil = hitung_lift_barang(
                alat, 
                request.form.get('kondisi_operasi_lift1'),
                request.form.get('pemeliharaan_mesin_lift1'),
                request.form.get('Cp_lift1'),
                request.form.get('H_lift1'),
                request.form.get('T1_lift1'),
                request.form.get('T3_lift1')
            )
        elif alat == 'Lift Barang, Tinggi 10-24 lantai (40-100 m), Bm 1,0 ton':
            hasil = hitung_lift_barang(
                alat,
                request.form.get('kondisi_operasi_lift2'),
                request.form.get('pemeliharaan_mesin_lift2'),
                request.form.get('Cp_lift2'),
                request.form.get('H_lift2'),
                request.form.get('T1_lift2'),
                request.form.get('T3_lift2')
            )
        elif alat == 'Lift Barang, Tinggi 10-24 lantai (40-100 m), Bm 2,0 ton':
            hasil = hitung_lift_barang(
                alat,
                request.form.get('kondisi_operasi_lift3'),
                request.form.get('pemeliharaan_mesin_lift3'),
                request.form.get('Cp_lift3'),
                request.form.get('H_lift3'),
                request.form.get('T1_lift3'),
                request.form.get('T3_lift3')
            )
        elif alat == 'Crane (Stationary Stand By) 40 Ton':
            opsi = request.form.get('opsi_crane1')
            if opsi == 'lokasi':
                hasil= hitung_lokasi_crane(
                    'Crane (Stationary Stand By) 40 Ton',
                    request.form.get('kondisi_operasi_crane1'),
                    request.form.get('pemeliharaan_mesin_crane1'),
                    request.form.get('V_crane1'),
                    request.form.get('lokasi_crane1')
                )
            else:
                hasil = hitung_lantai_crane(
                    'Crane (Stationary Stand By) 40 Ton',
                    request.form.get('kondisi_operasi_crane1'),
                    request.form.get('pemeliharaan_mesin_crane1'),
                    request.form.get('V_crane1'),
                    request.form.get('lantai_crane1')
                )
        elif alat == 'Crane (Tower), T=10-20 m, Arm 18 m, Bm 1,5 ton':
            opsi = request.form.get('opsi_crane2')
            if opsi == 'lokasi':
                hasil = hitung_lokasi_crane(
                    alat,
                    request.form.get('kondisi_operasi_crane2'),
                    request.form.get('pemeliharaan_mesin_crane2'),
                    request.form.get('V_crane2'),
                    request.form.get('lokasi_crane2')
                )
            else:
                hasil = hitung_lantai_crane(
                    alat,
                    request.form.get('kondisi_operasi_crane2'),
                    request.form.get('pemeliharaan_mesin_crane2'),
                    request.form.get('V_crane2'),
                    request.form.get('lantai_crane2')
                )
        elif alat == 'Crane (Tower), T=20-40 m, Arm 30 m, Bm 2,5 ton':
            opsi = request.form.get('opsi')
            if opsi == 'lokasi':
                hasil = hitung_lokasi_crane(
                    alat,
                    request.form.get('kondisi_operasi_crane3'),
                    request.form.get('pemeliharaan_mesin_crane3'),
                    request.form.get('V_crane3'),
                    request.form.get('lokasi_crane3')
                )
            else:
                hasil = hitung_lantai_crane(
                    alat,
                    request.form.get('kondisi_operasi_crane3'),
                    request.form.get('pemeliharaan_mesin_crane3'),
                    request.form.get('V_crane3'),
                    request.form.get('lantai_crane3')
                )
        else:
            hasil = {'error': 'Alat tidak dikenali'}
        
        return jsonify(hasil)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)