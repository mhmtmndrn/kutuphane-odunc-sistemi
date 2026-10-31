# ADR-0021: Affı yönetici bir borç kalemine yönelik olarak yapar

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 6. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

FR-14'e göre af kısmi olabilir, gerekçe ister ve borcu aşamaz. Ödemeler FIFO ile dağıtılıyor (ADR-0017). Affın da hangi kaleme düştüğü bilinmeli, çünkü AC-16'daki iptal ve iade hesapları kalem bazında yapılıyor.

## Değerlendirilen seçenekler

1. **Yönetici kalemi seçer** (seçildi): Hangi ceza ya da bedelin affedildiği açıktır ve denetim kaydı anlamlı olur. Af ekranına bir seçim adımı ekler.
2. **Ödemeler gibi FIFO:** Tek kural ve ek adım yok. Ancak affedilen kalem yöneticinin niyetinden farklı olabilir.

## Karar

- Af ekranında yönetici, üyenin ödenmemiş kısmı olan bir kalemini seçer, tutarı ve gerekçeyi girer.
- Tutar, seçilen kalemin ödenmemiş kısmını aşamaz. Böylece FR-14'teki "borcu aşamaz" koşulu da sağlanır.
- Af, `WAIVER` hareketi ve o kaleme tek bir dağıtım satırı olarak kaydedilir.
- Birden çok kalemin affı ayrı af hareketleriyle yapılır.

## Sonuçlar

- **Olumlu:** Kalem bazında hesap tutarlı kalır. Denetim kaydı hangi borcun affedildiğini gösterir.
- **Olumsuz / riskler:** Toplu af için birden çok işlem gerekir; tasarım ölçeğinde kabul edilebilir.

## İzlenebilirlik

- **Gereksinim:** FR-14, FR-17, FR-26
- **Bağlantılı:** ADR-0017, ADR-0020
