# ADR-0018: Saklama süresi dolan ödünçlerin bağı koparılır, sayı üyedeki arşiv sayacında kalır

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 4. tur. Kullanıcı soru penceresinden seçti. SRS'teki AC-25'e not eklenir.

## Bağlam

FR-25, iadesinin üzerinden saklama süresi geçen ödünçlerin üye bağının kaldırılmasını istiyor. AC-25 ise anonimleştirilen üyenin ödünç sayısının raporlarda kalmasını istiyor. Bağ kopunca eski ödünçler sayımdan düşeceği için iki kural birbiriyle çelişiyor.

## Değerlendirilen seçenekler

1. **Bağ kopar, üyede sayaç tut** (seçildi): Bağ koparılırken üyedeki arşivlenmiş ödünç sayısı artırılır. FR-25 aynen kalır.
2. **Anonim üyenin bağı kalsın:** FR-25 metni değişir. Aktif üyede sayım yine düşer.
3. **AC-25'ten sayımı çıkar:** En basit model. Kişi başı ödünç sayısı saklama süresi dolunca kaybolur.

## Karar

- Anonimleştirme görevi, iadesinin üzerinden saklama süresi geçen her ödünç için aynı işlem içinde üç şey yapar:
  - Ödüncün üye bağını boşaltır.
  - Üyenin `archived_loan_count` sayacını bir artırır.
  - O ödünce bağlı borç hareketlerinin ödünç bağını boşaltır.
- Üyenin toplam ödünç sayısı, bağlı ödünç sayısı ile arşiv sayacının toplamıdır.
- Dolaylı yoldan yeniden bağ kurulmasını önlemek için denetim kaydı ve hatırlatma kaydı üye ile ödünç arasındaki ilişkiyi tekrar etmez.
- Borç hareketleri üyeye bağlı kalır, böylece tutarlar korunur (FR-25).

## Sonuçlar

- **Olumlu:** Gizlilik kuralı ve istatistik birlikte sağlanır. Görev idempotenttir, çünkü yalnız bağı dolu ödünçleri işler.
- **Olumsuz / riskler:**
  - Saklama süresinden sonra bulunan kayıp bir nüshanın bedeli artık ödünç üzerinden bulunamaz; yönetici iptali elle yapar.
  - Sayaç yalnız bu görevle değiştirilmelidir.

## İzlenebilirlik

- **Gereksinim:** FR-25; AC-25; NFR-08
- **Bağlantılı:** ADR-0007
