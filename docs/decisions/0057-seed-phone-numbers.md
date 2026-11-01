# ADR-0057: Tohum verideki telefonlar "000" önekli sahte numaralardır

- **Durum:** Kabul edildi (2026-11-01)
- **Kaynak:** Kullanıcı, 2026-11-01'de `feature/seed-load` (G17–G18) açılış isteminde onayladı. Kaynak bulgu TC-234.

## Bağlam

- FR-01'e göre üyenin adı ve telefonu zorunludur; tohum veri her üyeye bir telefon yazar.
- AC-29 ve TC-234, tohum üyelerinin gerçek bir kişiyi göstermemesini ister. Adlar sabit listelerden gelir ve tek başına kimseyi göstermez; ama rastgele üretilmiş geçerli biçimli bir cep telefonu (ör. `0555 …`) gerçek bir aboneye denk gelebilir. Demo ve yük verisi sunucuda, ekran görüntülerinde ve hatırlatma denemelerinde görünebilir.
- E-postalar zaten `@example.invalid` ile biter ve hiçbir alıcıya ulaşmaz (plan G17).

## Değerlendirilen seçenekler

1. **"000" önekli sahte numara** (seçildi): Türkiye'de hiçbir alan kodu ya da operatör öneki "00" ile başlamaz; "000" ile başlayan bir numara aranabilir bir aboneye denk gelmez. Biçim ekranda gerçek telefon gibi görünür ve aramayı (`phone_digits`) sınar.
2. **Gerçek biçimli rastgele cep numarası:** Daha gerçekçi görünür, ama bir aboneye denk gelebilir (TC-234 başarısız olur).
3. **Telefonsuz üye:** FR-01'in zorunlu alanını bozar ve telefon araması sınanamaz.

## Karar

- Her tohum üyesinin telefonu `000 ddd dd dd` biçimindedir (ör. `000 123 45 67`): "000" ve ardından 7 rastgele hane; toplam 10 rakam. Aynı tohum verisinde iki üyenin numarası aynı olmaz.
- `phone_digits` mevcut domain fonksiyonuyla hesaplanır (`0001234567`).
- Bu kural iki profil (demo, load) için de geçerlidir.

## Sonuçlar

- **Olumlu:** Tohum telefonları hiçbir gerçek aboneye denk gelmez; TC-234 örneklem incelemesinde telefon için ayrıca arama gerekmez.
- **Olumsuz / riskler:** Bütün tohum telefonları aynı önekle başladığı için "000" ile yapılan telefon araması 50 sonuç sınırına takılır; demo ve yükte gerçekçi arama için sonraki hanelerle aramak gerekir.

## İzlenebilirlik

- **Gereksinim:** FR-01, FR-29, NFR-08; AC-29. Plan G17, §11 (G17–G18 açılış kararları).
- **Bağlantılı:** ADR-0033, ADR-0038
