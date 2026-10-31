# ADR-0046: Ödünç ekranında üye alanına girilen rakam biçimine göre yorumlanır

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 5. tur. Kullanıcı soru penceresinden seçti (inşa kontrolü bulgusu §8.1-12).

## Bağlam

Ödünç ekranında üye alanına yalnız rakamdan oluşan bir değer, üye no olarak yorumlanıyordu. Bu yüzden iki hata oluşuyordu:

- Nüsha barkodu (8 hane, baştaki sıfırlarla) yanlışlıkla üye alanına okutulursa, örneğin 42 numaralı üye açılıyordu.
- Telefon numarası girilirse "Üye bulunamadı" çıkıyordu.

## Değerlendirilen seçenekler

1. **Biçime göre ayırmak** (seçildi).
2. **Mevcut davranış:** Yanlış üye açılabilir.

## Karar

- `circulation.domain.classify_member_input(raw: str) -> MemberInput` girdiyi önce temizler: boşluk, tire ve parantezler atılır. Ardından girdiyi şöyle sınıflandırır:
  - Yalnız rakam, 8 hane ve ilk hane "0" ise **nüsha barkodu** sayılır. Üye açılmaz ve "Bu bir nüsha barkodu. Üye kartını okutun." uyarısı gösterilir.
  - Yalnız rakam ve 10–11 hane ise **telefon** sayılır. Telefonla arama yapılır ve sonuçlar `?uye=<no>` bağlantıları olarak gösterilir.
  - Yalnız rakamdan oluşan diğer girdiler **üye no** sayılır.
  - Rakam dışı karakter içeren girdi **ad araması**dır (mevcut davranış).
- Kurallar ve temizlenen karakterler KL-35'tedir.

## Sonuçlar

- **Olumlu:** Yanlış okutmada yanlış üye açılmaz. Telefonla bulma masada mümkün olur.
- **Olumsuz / riskler:** 10 haneye ulaşan üye no telefon gibi yorumlanır. Tasarım ölçeği 5.000 üye olduğundan bu sınıra ulaşılmaz.

## İzlenebilirlik

- **Gereksinim:** FR-11, FR-01; AC-11
- **Bağlantılı:** ADR-0032; KL-10
