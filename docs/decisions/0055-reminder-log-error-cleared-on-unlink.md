# ADR-0055: Ödüncün üye bağı koparılırken hatırlatma kaydının hata metni temizlenir

- **Durum:** Kabul edildi (2026-11-01)
- **Kaynak:** Kullanıcı, 2026-11-01'de `feature/operations` (G14–G16) açılış isteminde onayladı.

## Bağlam

- ADR-0018'e göre saklama süresi dolan ödüncün üye bağı koparılır. Denetim kaydı ve hatırlatma kaydı üye ile ödünç arasındaki ilişkiyi tekrar etmemelidir.
- G13'te `reminder_log.error` alanı SMTP hata metnini `f"{type(exc).__name__}: {exc}"` biçiminde saklar (plan §11, G13 küçük karar 5). `SMTPRecipientsRefused` gibi hatalar alıcının e-posta adresini metne yazar.
- `reminder_log` satırı ödünce bağlı kalır. Bağ koparıldıktan sonra hata metnindeki e-posta adresi, ödüncü dolaylı yoldan bir kişiye yeniden bağlar ve saklama süresi dolmuş bir kişisel veriyi tutar (NFR-08).

## Değerlendirilen seçenekler

1. **Bağ koparılırken `error` alanını NULL yapmak** (seçildi): Aynı işlemde o ödünce ait bütün `reminder_log` satırlarının `error` alanı NULL olur; tür, durum ve tarihler kalır. Basit ve kesindir; hata ayrıntısı zaten yalnız pencere içindeki yeniden deneme için anlamlıdır.
2. **G13'ün `error_text`'inde adresi ayıklamak:** Kayıt anında e-posta adresleri metinden çıkarılır. Hata ayrıntısı korunur, ama adresin her biçimini (SMTP sunucusunun kendi metni dahil) yakalamak garanti değildir ve G13'ün onaylanmış davranışı değişir.
3. **Olduğu gibi bırakmak:** Kod değişmez; saklama süresi dolmuş e-posta adresi süresiz kalır.

## Karar

- G15'te bir ödüncün üye bağı koparılırken (ADR-0018) aynı `transaction.atomic()` içinde `ReminderLog.objects.filter(loan=loan).update(error=None)` çalışır.
- `kind`, `status`, `due_on`, `sent_at` ve `triggered_by` değişmez; satır silinmez.
- G13'ün hata metni biçimi değişmez.
- Bu, architecture §3'e `operations → notifications` okunu ekler (yalnız `notifications.models.ReminderLog`). `notifications` `operations`'ı import etmediği için döngü oluşmaz.

## Sonuçlar

- **Olumlu:** Saklama süresi dolan ödünçte e-posta adresi hatırlatma kaydında da kalmaz; ADR-0018'deki "dolaylı bağ kurulmaz" kuralı hatırlatma kaydı için de sağlanır.
- **Olumsuz / riskler:** Bağı koparılmış ödüncün eski bir gönderim hatasının nedeni artık görülemez. Saklama süresi (en az 1 yıl) hatırlatma pencerelerinden çok uzun olduğu için bu ayrıntıya ihtiyaç kalmaz.

## İzlenebilirlik

- **Gereksinim:** FR-25, NFR-08; AC-25. Plan G15, §11 (G14–G16 açılış kararları).
- **Bağlantılı:** ADR-0018, ADR-0039, ADR-0045
