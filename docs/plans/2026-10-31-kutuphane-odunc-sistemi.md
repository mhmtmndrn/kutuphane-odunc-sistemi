# Görev planı: Kütüphane ödünç alma sistemi

- **Tarih:** 2026-10-31
- **İz:** Tam
- **Durum:** Faz 1 tamamlandı (SRS onaylandı 2026-10-31); sıradaki faz 2 (araştırma)

## 1. Süreç uyarlaması

- **İstek:** Küçük bir kütüphane için web tabanlı kitap ödünç alma sistemi: üyeler, kitaplar, ödünç verme ve iade, gecikme cezası.
- **Bağlam:** Gerçek kullanım (ürün modu). Kullanıcı yalnız kütüphane personeli; üyeler sisteme giriş yapmaz. Dağıtım: yerel sunucu, LAN (faz 1). Süre kısıtı yok. Dil, framework ve veritabanı seçilmedi; faz 3'te alternatiflerle sorulacak.
- **Artefaktlar:** `docs/srs.md`, `docs/architecture.md`, `docs/data-design.md`, `docs/test-plan.md`, `docs/risk-register.md`, bu görev planı, `docs/decisions/` altında ADR'ler.
- **Test yaklaşımı:** TDD.
- **Fırsat taraması:** 2026-10-31, ürün modu.
  - **Barkodla ödünç/iade masası:** kapsamda (FR numarası faz 1'de verilecek). Minimum sürüm: barkod okutmaya göre tasarlanmış ödünç/iade alanları (USB okuyucu klavye gibi çalışır), nüsha başına benzersiz kod, toplu etiket basmak için PDF. B planı: aynı alanlara elle kod girişi ya da arama. Not: nüsha düzeyinde takip gerektirir; veri tasarımında kullanıcıya sorulacak.
  - **Otomatik son tarih ve gecikme hatırlatması (e-posta):** kapsamda (FR numarası faz 1'de verilecek). Minimum sürüm: günde bir kez çalışan görev; son tarihe 2 gün kala ve gecikmenin 1. gününde şablonlu e-posta, gönderim kaydı. B planı: personelin tetiklediği "hatırlatma gönder" düğmesi ve uygulama içinde geciken ödünç listesi. Açık noktalar: e-posta servisi seçimi (faz 3'te ADR), KVKK açık rızası (faz 1), uygulama sürekli çalışmıyorsa zamanlanmış görevin atlanması.
  - **ISBN ile otomatik katalog doldurma:** fizibilite. Faz 2'de araştırılacak soru: Open Library, Google Books ve benzeri ücretsiz meta veri API'leri Türkçe kitapları ne oranda kapsıyor? Bunu 20–30 örnek ISBN ile ölç; lisans, rate limit ve kullanım şartlarını kontrol et. Kullanıcı bulgulardan sonra karar verecek. B planı: elle giriş.
  - **Gerek yok (yeniden önerilmeyecek):** `ml-recsys` (üye arayüzü yok, etkileşim verisi az), `ml-predict` (veri az, hatırlatma kuralla çözülüyor), `llm-feature`, `llm-rag`, `agent-*`, `ml-pretrained` (kapaktan OCR; ISBN sorgusu daha ucuz), `opt-*`, `sys-realtime`.

## 2. Dokunulan dokümanlar

| Doküman | Değişiklik |
|---|---|
| docs/srs.md | Faz 1'de oluşturuldu, onaylandı (2026-10-31) |
| docs/architecture.md | Faz 3'te oluşturulacak |
| docs/data-design.md | Faz 3'te oluşturulacak |
| docs/test-plan.md | Faz 4'te oluşturulacak |
| docs/risk-register.md | Faz 1–4'te oluşturulacak |

## 3. Kararlar

Henüz ADR yok. Faz 0'da verilen süreç kararları: Tam iz, yukarıdaki artefakt seti, TDD.

Faz 1 kapsam kararları SRS'te kaynaklarıyla birlikte duruyor (tek üye tipi, yönetici ve görevli rolleri, rezervasyon yok, yerel sunucu, ayarlanabilir kurallar, KVKK). Stack ve servis seçimleri faz 3'te ADR olacak.

**Küçük kararlar (onaylandı 2026-10-31):**

1. Varsayılan ayarlar: günlük ceza 5,00 TL; ödünç başına ceza üst sınırı 150,00 TL; borç eşiği 50,00 TL (eşik dahil engeller); saklama süresi 2 yıl.
2. Gecikme günü = iade tarihi − son tarih (takvim günü); son tarihte iade 0 gün.
3. Uzatmada yeni son tarih = mevcut son tarih + ödünç süresi, kapalı gün kaydırmasıyla.
4. Kayıp ve hasar işaretlemesini yalnız yönetici yapar.
5. Hasarlı nüsha: yönetici rafa döndürür (onarıldı) ya da kayıttan düşer (durum: Kayıttan düşmüş).
6. Açık ödüncü olan üye pasifleştirilemez; borcu olan üye uyarıyla pasifleştirilebilir.
7. Hatırlatma görevi her gün 09:00'da çalışır; ödünç ve hatırlatma tipi başına en fazla bir gönderim.
8. Üye no otomatik ve sıralı; nüsha barkodu Code 128, 8 haneli sıralı; etiket PDF'i A4, sayfa başına 24 etiket (3×8).
9. Parola en az 10 karakter; hesap kilidi 15 dakika.
10. Saat dilimi Europe/Istanbul; gün sınırı yerel gece yarısı.
11. Af kısmi olabilir (tutar ≤ borç); borçtan fazla ödeme kabul edilmez.

## 4. Görevler

Faz 4'te yazılacak.

## 5. Testler

Faz 4'te yazılacak.

## 6. Riskler

| ID | Risk | Olasılık | Etki | Tetik | Azaltma |
|---|---|---|---|---|---|
| R-01 | ISBN API'leri Türkçe kitapları yeterince kapsamıyor | Orta | Düşük | Faz 2 ölçümünde düşük isabet | Elle giriş (varsayılan çözüm) |
| R-02 | Hatırlatma e-postaları spam'e düşüyor ya da zamanlanmış görev atlanıyor | Orta | Orta | Uygulama sürekli çalışmıyor; SPF/DKIM yok | Elle tetiklenen hatırlatma ve uygulama içinde geciken ödünç listesi |
| R-03 | Kütüphanede barkod okuyucu ya da etiket yazıcısı yok | Düşük | Düşük | Kurulum sırasında donanım eksik | Elle kod girişi ve arama |
| R-04 | Sunucu ve harici yedek diski aynı binada; yangın ya da hırsızlıkta ikisi birden gider | Düşük | Yüksek | Bina olayı | Yedeğin bir kopyasını periyodik olarak bina dışına taşıma; faz 3'te kullanıcıya sorulacak |
| R-05 | Varsayılan saklama süresi kurumun KVKK politikasıyla çelişiyor | Orta | Orta | Kurum teyidi farklı süre veriyor | Süre ayar olduğu için yalnız değer değişir (FR-23) |

## 7. İzlenebilirlik

Faz 4'te doldurulacak.

## 8. Tutarlılık kontrolü

Faz 4'te yapılacak.

## 9. Önerilen commit noktaları

- Kök commit (`main`): `chore: set up project docs skeleton`. Onaylandı 2026-10-31; AGENTS.md'deki dal kuralına tek istisna.
- `feature/requirements`: `docs: add approved SRS and phase 1 plan updates`.

## 10. Onay

Henüz yok.

## 11. Sapmalar

Yok.
