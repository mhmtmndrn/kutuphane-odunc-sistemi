# ADR-0006: Bina dışı yedek için haftalık şifreli USB rotasyonu

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 2. tur. Kullanıcı soru penceresinden seçti. R-04'ü azaltır.

## Bağlam

FR-28'deki günlük yedek, sunucuyla aynı binadaki harici diske alınıyor. Yangın ya da hırsızlıkta ikisi birden kaybolur (R-04). SRS bölüm 7 bulutu dışlıyor.

## Değerlendirilen seçenekler

1. **Haftalık şifreli USB rotasyonu** (seçildi): Sistem haftada bir şifreli yedek dosyası üretir. Yönetici bunu USB belleğe alıp bina dışında saklar. Bina olayında RPO ≤ 7 gün olur. Bulut gerekmez.
2. **Riski kabul et ve belgele:** Ek iş yok, ama bina olayında tüm veri kaybolur.
3. **Şifreli bulut kopyası:** Otomatik. Ancak "bulut yok" kısıtını değiştirmeyi ve yurt dışı sağlayıcıda KVKK md. 9 yükümlülüğünü gerektirir.

## Karar

- Sistem haftada bir, son günlük yedekten şifreli bir dışa aktarma dosyası üretir. Şifreleme ADR-0011'e göre yapılır.
- Dosya bilinen bir klasöre yazılır.
- Yönetici dosyayı en az iki USB bellek arasında dönüşümlü kopyalar ve bina dışında saklar.
- Yönetici arayüzünde son dışa aktarmanın tarihi görünür. 7 günü geçen bir dışa aktarma uyarı olarak gösterilir.

## Sonuçlar

- **Olumlu:** R-04'ün etkisi "tüm veri" yerine "en fazla bir haftalık veri" olur. Bulut ve yurt dışı aktarım yok.
- **Olumsuz / riskler:**
  - İnsan adımına bağlıdır; uyarı unutulma riskini azaltır ama kaldırmaz.
  - Şifre parolasının kaybı yedeği işe yaramaz hale getirir.
  - Bu davranış SRS'te henüz bir FR değil. SRS'e eklenmesi kullanıcıya sorulacak.

## İzlenebilirlik

- **Gereksinim:** FR-28; NFR-03; R-04
- **Bağlantılı:** ADR-0002, ADR-0007, ADR-0011
