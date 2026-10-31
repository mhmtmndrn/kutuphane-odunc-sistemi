# ADR-0032: Üye kartında ad bulunmaz; kayıp kart aynı numarayla yeniden basılır

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 2. tur. Kullanıcı soru penceresinden iki ayrı soruyla seçti. ADR-0025'te faz 4'e bırakılan kart içeriği ve yeniden basım kararları bu ADR'yle verildi.

## Bağlam

FR-38 üye kartı PDF'ini kapsama aldı. Kartta ad bulunması kişisel verinin açığa çıkması anlamına gelir (NFR-08). Kaybolan kart için bir akış tanımlı değildi.

## Değerlendirilen seçenekler

- Kart içeriği:
  1. **Ad yok** (seçildi): Kartta kütüphane adı, üye no ve barkod bulunur. Kayıp kart kişisel veri taşımaz.
  2. **Ad soyad basılır:** Kart kolay tanınır, ama kayıp kartta ad ve üye no birlikte açığa çıkar.
- Kayıp kart:
  1. **Aynı numarayla yeniden bas** (seçildi): Veri modeli değişmez; eski kart geçerli kalır.
  2. **Kart sürümüyle iptal:** Barkod "üye no + sürüm" taşır ve eski kartlar reddedilir. Bu da veri modeline bir alan, barkod biçimine bir kural ve yeni test durumları ekler.

## Karar

- Kartta yalnız `library_settings.library_name` (ADR-0035), "Üye No" etiketiyle üye no ve üye no'yu taşıyan Code 128 barkod bulunur.
- Kayıp kartta personel, FR-38 ile aynı üyenin kartını yeniden basar. Ayrı bir akış ya da kayıt yoktur.
- Kaybolan kartın kötüye kullanımı, ödünç ekranında üyenin adının görünmesi ve görevlinin üyeye adını sorması ile azaltılır. Bu adım kullanım kılavuzuna yazılır.

## Sonuçlar

- **Olumlu:** Kart kişisel veri taşımaz, veri modeli değişmez, efor en düşük düzeydedir.
- **Olumsuz / riskler:** Eski kart iptal edilemez. Küçük kütüphane ölçeğinde kabul edildi.

## İzlenebilirlik

- **Gereksinim:** FR-11, FR-38, NFR-08; AC-31
- **Bağlantılı:** ADR-0025, ADR-0035
