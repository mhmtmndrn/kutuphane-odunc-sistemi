# Durum (devir notu)

- **Güncelleme:** 2026-10-31
- **Aşama:** eng-process faz 1 (gereksinimler) tamamlandı, SRS onaylandı. Sıradaki faz 2 (araştırma). Plan: `docs/plans/2026-10-31-kutuphane-odunc-sistemi.md`
- **Dal:** `feature/requirements` (kök commit `main` üzerinde)

## Sıradaki adım

`eng-process` skill'ini çalıştır; plan dosyasından devam ederek **faz 2'ye (araştırma)** gir. Önce `phases/02-research.md` dosyasını oku. İki soru var, ikisi de `research` skill'iyle `docs/research/` altına rapor olarak yazılacak:

1. **ISBN meta veri API'leri (FR-30, R-01):** Open Library, Google Books ve benzeri ücretsiz kaynaklar Türkçe kitapları ne oranda kapsıyor? 20–30 örnek ISBN ile ölç; lisans, rate limit ve kullanım şartlarını kontrol et. Kullanıcı bulgulara göre FR-30'u (Could) tutar ya da düşürür.
2. **Demo kitap veri seti (FR-29):** Lisansı uygun, Türkçe kitap içeren açık bir veri seti var mı (örn. Open Library dump'ları)? Yoksa sentetik veri üretilecek. Üye verisi her durumda sentetik.

İki soru birbirinden bağımsız; paralel `researcher` subagent'larına uygun.

## Açık sorular ve riskler

- E-posta gönderim yolu (kurum SMTP ya da servis) ve LAN içinde HTTPS: faz 3'te ADR (SRS açık soru 3, 4).
- Sunucu donanımı ve işletim sistemi belli değil; stack Windows ve Linux'ta çalışmalı (SRS bölüm 7).
- Varsayılan 2 yıllık saklama süresi kurumun KVKK politikasıyla teyit edilmeli (SRS açık soru 6, R-05).
- R-04: sunucu ve yedek diski aynı binada; bina dışı yedek faz 3'te kullanıcıya sorulacak.
- Dil, framework ve veritabanı faz 3'te alternatiflerle sorulacak (ADR). Stack ADR'sinden sonra araç taraması yenilenecek (auto memory).

## Nerede kaldık

- SRS: [docs/srs.md](srs.md), onaylandı 2026-10-31. 29 FR kapsam içi (22 Must, 7 Should, 1 Could), 6 Won't, 13 NFR, her FR için Gherkin kabul senaryosu.
- Faz 1 kararları: tek üye tipi ve ayarlanabilir kurallar (14 gün / 3 kitap), 1 uzatma, günlük ceza ve üst sınır, kapalı günlerde son tarih kayması, borç eşiğiyle engelleme, kısmi ödeme ve gerekçeli af, kayıp ve hasar bedeli, yönetici ve görevli rolleri, rezervasyon yok, yerel sunucu (LAN), asgari üye verisi, e-posta rızası, ayarlı anonimleştirme, günlük harici disk yedeği, Türkçe masaüstü arayüz, ölçek 20 bin nüsha / 5 bin üye / 5 personel.
- 11 küçük karar onaylandı; görev planının 3. bölümünde.
- Henüz ADR ya da kod yok.

## Son güncellemeden bu yana yapılanlar

- 2026-10-31: Faz 1 görüşmesi (6 tur), `docs/srs.md` yazıldı ve onaylandı.
- 2026-10-31: Görev planı güncellendi: küçük kararlar, R-04 ve R-05.
- 2026-10-31: Kök commit `main` üzerinde; faz 0–1 dokümanları `feature/requirements` dalında.

## Nasıl çalıştırılır ve test edilir

Henüz kod yok; stack faz 3'te seçilecek.
