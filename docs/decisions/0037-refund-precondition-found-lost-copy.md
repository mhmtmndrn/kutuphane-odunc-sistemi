# ADR-0037: Para iadesi yalnız bulunan kayıp nüshanın bedeline yapılır

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 5. tur. Kullanıcı soru penceresinden seçti: önce ön koşulu (inşa kontrolü bulgusu §8.1-1), ardından iki ayrı soruyla izin nerede tutulacağını ve bağı koparılmış bedeli.

## Bağlam

- Eski I5 (data-design §2.5), REFUND'u yalnız `CANCELLATION` almış bir bedele izin veriyordu. Bedel tamamen ödenmişse `cancel_unpaid` hiçbir şey yazmaz; bu yüzden para iadesi imkânsızdı. Oysa FR-16 ve G12 personeli para iadesine yönlendiriyor. İnşa kontrolü bunu Yüksek önemde bir çelişki olarak bildirdi.
- "Nüsha bulundu" bilgisi kalıcı olarak tutulmuyordu. Nüshanın durum alanı, nüsha bulunup sonra yeniden kaybolduğunda yanlış sonuç verir.
- Saklama görevi ödüncün bağını koparınca (ADR-0018) `ledger_entry.loan_id` NULL olur ve ön koşul doğrulanamaz.

## Değerlendirilen seçenekler

- Ön koşul: kullanıcı, "kalemin ödüncü LOST ile kapandı ve nüsha bulundu" tanımını seçti.
- "Bulundu" izi:
  1. **`loan.copy_found_on` sütunu** (seçildi): Kesin ve sorgulanabilir, test etmesi kolay. Şemaya NULL olabilen bir sütun eklenir.
  2. **Denetim kaydından türetmek:** Şema değişmez, ama denetim kaydı iş kuralının kaynağı olur.
  3. **Nüshanın şu anki durumu:** En basit seçenek. Nüsha yeniden kaybolursa eski bedelin iadesi yanlışlıkla engellenir.
- Bağı koparılmış bedel:
  1. **İade yapılamaz** (seçildi): Bağ, ödünç kapandıktan en az 2 yıl sonra kopar; durum çok nadirdir.
  2. **Yönetici gerekçeyle girer:** I5'e bir istisna ve bir form eklenir.

## Karar

- **I5 (yeni):** Bir bedel kalemi için para iadesi toplamı, o kaleme yapılmış ödeme (PAYMENT) dağıtımlarının toplamını aşamaz. REFUND yalnız şu koşulları taşıyan bir bedel için girilebilir: `loan_id` dolu, ödüncü `close_reason = 'LOST'` ile kapanmış ve `loan.copy_found_on` dolu.
- **Şema:** `loan.copy_found_on date NULL` eklenir. Kısıt: `CHECK (copy_found_on IS NULL OR (close_reason = 'LOST' AND copy_found_on >= closed_on))`.
- **`mark_found`:** Hedef, nüshanın en son ödüncüdür (en büyük `id`). Bu ödüncün `close_reason` değeri LOST ve `copy_found_on` değeri NULL ise iki şey yapılır: `copy_found_on = bugün` yazılır ve bağlı bedelin ödenmemiş kısmı iptal edilir. Bu koşul sağlanmıyorsa nüsha raftan kaybolmuştur; iki adım da atlanır.
- **Red:** Koşulu sağlamayan bedel için para iadesi "Para iadesi yalnız bulunan kayıp nüshanın bedeli için yapılabilir" mesajıyla reddedilir. Bağı koparılmış bedel (`loan_id` NULL) de bu mesajı alır.

## Sonuçlar

- **Olumlu:** İnşa kontrolü bulgusu 1 çözülür. Tamamen ödenmiş bedel de iade edilebilir. "Bulundu" bilgisi kalıcı ve sorgulanabilirdir.
- **Olumsuz / riskler:** Şemaya bir sütun eklenir. Bağı koparılmış bedel için para iadesi sistemde yapılamaz. Böyle bir durum kasadan elle çözülür ve sistemde izi kalmaz.

## İzlenebilirlik

- **Gereksinim:** FR-16, FR-26; AC-16
- **Bağlantılı:** ADR-0018, ADR-0020, ADR-0027, ADR-0041
