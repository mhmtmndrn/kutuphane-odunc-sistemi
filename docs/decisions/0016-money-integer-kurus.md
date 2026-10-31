# ADR-0016: Para tutarları tam sayı kuruş olarak saklanır

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 4. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

NFR-12, para hesaplarının kuruş hassasiyetinde ve kayan nokta hatası olmadan yapılmasını istiyor. Veritabanı SQLite (ADR-0002). Django'nun `DecimalField`'ı SQLite'ta NUMERIC affinity ile saklanıyor. Bu yüzden ondalıklı değerler REAL olarak yazılabiliyor ve SQL'deki `SUM` kayan nokta sonucu döndürüyor.

## Değerlendirilen seçenekler

1. **Tam sayı kuruş** (seçildi): `IntegerField`; örneğin 1500 değeri 15,00 TL demektir. SQL toplamları dahil her işlem tam sayıdır. Gösterim için bir çevirme katmanı gerekir.
2. **DecimalField:** Kodda doğal `Decimal` tipi kullanılır. Ancak SQLite'ta toplamlar kayan noktaya düşebildiği için toplamları Python'da yapmak gerekir.

## Karar

- Bütün tutar sütunları `_kurus` sonekli, negatif olmayan tam sayılardır. Borç ve alacak yönünü tutarın işareti değil hareket türü belirler.
- Ayarlardaki günlük ceza, ceza üst sınırı ve borç eşiği de kuruş olarak tutulur.
- Arayüzde giriş ve gösterim "15,00 TL" biçimindedir. TL ile kuruş arasındaki çevrim tek bir yardımcı modülde yapılır. Girişte kuruştan küçük basamak reddedilir.
- Kodda tutar için `float` kullanılmaz.

## Sonuçlar

- **Olumlu:** Kayan nokta hatası yapısal olarak imkansız. SQL toplamları güvenilir.
- **Olumsuz / riskler:** Çevirme katmanı unutulursa ekranda 1500 görünür. Biçimlendirme testleriyle ve şablon filtresiyle önlenir.

## İzlenebilirlik

- **Gereksinim:** FR-12, FR-13, FR-14, FR-15, FR-17, FR-23; NFR-12
- **Bağlantılı:** ADR-0002, ADR-0017
