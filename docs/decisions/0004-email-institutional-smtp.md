# ADR-0004: Hatırlatma e-postaları kurum SMTP hesabıyla gönderilir

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 1. tur. Kullanıcı soru penceresinden seçti. SRS açık soru 3'ü kapatır.

## Bağlam

FR-18 ve FR-19 şablonlu hatırlatma e-postası istiyor. R-02'ye göre e-postalar spam'e düşebilir. Üye e-posta adresi kişisel veridir; KVKK açısından yurt dışı aktarım (md. 9) yükümlülük doğurur.

## Değerlendirilen seçenekler

1. **Kurum SMTP hesabı** (seçildi): Ücretsiz. Kurum alan adının SPF/DKIM kayıtlarıyla teslim oranı iyi. Veri kurumun mevcut e-posta sağlayıcısında kalır. Kurumun bir gönderen hesabı açması gerekir.
2. **Transactional servis (Brevo, Mailjet, SES vb.):** Teslim oranı yüksek. Ancak yurt dışı servis KVKK md. 9 yükümlülüğü, DNS ayarı ve kota sınırı getirir.
3. **Kişisel Gmail ve uygulama şifresi:** En hızlı kurulum. Kişisel hesaba bağımlılık, günlük gönderim limiti ve yurt dışı aktarım sorunu var.

## Karar

- E-posta, Django'nun SMTP backend'iyle gönderilir. Varsayılan port 587 ve STARTTLS'tir.
- Sunucu, kullanıcı adı, parola ve gönderen adresi depoya girmeyen bir yapılandırmadan okunur. Sağlayıcı değişikliği yalnız yapılandırma değişikliği olarak kalır.
- Geliştirmede ve testlerde e-posta gerçek sunucuya gitmez. Bellek ya da konsol backend'i kullanılır.

## Sonuçlar

- **Olumlu:** Ek maliyet ve yurt dışı aktarım yok. R-02'nin spam bileşeni azalır.
- **Olumsuz / riskler:**
  - Kurumdan hesap alınması bir kurulum ön koşuludur.
  - SMTP kimlik bilgisi sunucuda durur; dosya izinleri kısıtlanmalı.
  - Kurumun sağlayıcısı yurt dışındaysa (örneğin Google Workspace) aktarım konusu kurumun mevcut KVKK değerlendirmesine dahildir.

## İzlenebilirlik

- **Gereksinim:** FR-18, FR-19; R-02
- **Bağlantılı:** ADR-0007
