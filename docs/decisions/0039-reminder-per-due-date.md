# ADR-0039: Hatırlatma tekrar engeli son tarih başınadır

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 5. tur. Kullanıcı soru penceresinden seçti (inşa kontrolü bulgusu §8.1-3).

## Bağlam

Benzersiz kısıt `(loan_id, kind) WHERE status = 'SENT' AND kind <> 'MANUAL'`, bir ödünce her türden en fazla bir otomatik hatırlatma gönderilmesine izin veriyordu. Uzatılan ödünç, yeni son tarihi için yeniden DUE_SOON alamıyordu.

## Değerlendirilen seçenekler

1. **`reminder_log.due_on` ve son tarih başına tekrar engeli** (seçildi): Uzatılan ödünç yeni son tarihi için yeniden hatırlatma alır. Şemaya bir sütun eklenir.
2. **Mevcut kısıt:** Uzatılan ödünç ikinci hatırlatmayı almaz.

## Karar

- `reminder_log.due_on date NOT NULL` eklenir. Değeri, deneme anındaki `loan.due_on` değeridir; MANUAL kayıtlarda da doldurulur.
- Kısmi benzersiz indeks şu olur: `UNIQUE(loan_id, kind, due_on) WHERE status = 'SENT' AND kind <> 'MANUAL'`.
- S6'daki `NOT EXISTS reminder_log` koşulu `due_on = loan.due_on` eşleşmesini de arar.
- FR-18'in tekrar cümlesi şöyle değişir: "aynı hatırlatmayı aynı ödünç ve aynı son tarih için ikinci kez göndermemeli".

## Sonuçlar

- **Olumlu:** Uzatmadan sonra üye yeni son tarihi için uyarılır.
- **Olumsuz / riskler:** Şemaya bir sütun eklenir; S6 sorgusu bir koşul daha alır, ama maliyeti değişmez.

## İzlenebilirlik

- **Gereksinim:** FR-18, FR-10; AC-18
- **Bağlantılı:** ADR-0007; faz 3 küçük karar 7
