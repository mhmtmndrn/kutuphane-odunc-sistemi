# ADR-0056: Bulut oturumunda Open Library'ye erişilemezse demo kitap dosyası yerel doğrulamada çekilir

- **Durum:** Kabul edildi (2026-11-01)
- **Kaynak:** Kullanıcı, 2026-11-01'de `feature/seed-load` (G17–G18) açılış isteminde onayladı.

## Bağlam

- ADR-0033'e göre demo kitapları `scripts/fetch_demo_books.py` ile Open Library'den bir kez çekilir, filtrelenir ve `seed/books_openlibrary.json` olarak depoya girer. `load_seed_data` yalnız bu dosyayı okur; dosyada 300'den az kayıt varsa eksik kısım sentetik kitaplarla tamamlanır.
- G17 bulut oturumunda uygulanır. Bulut ortamının ağ politikası her dış sunucuya izin vermeyebilir; Open Library engelliyse dosya oturumda üretilemez.
- Testler ağa çıkmaz (test planı §5); `load_seed_data` testlerinin gerçek dosyaya ihtiyacı yoktur.

## Değerlendirilen seçenekler

1. **Dosya olmadan devam etmek, gerçek dosyayı yerel doğrulamada çekmek** (seçildi): Oturum betiği çalıştırmayı dener. Ağ engelliyse dal dosyasız ilerler; testler küçük bir örnek dosyayla koşar ve ADR-0033'teki sentetik tamamlama sınanır. Kullanıcı yerel doğrulamada betiği çalıştırır ve çıktıyı aynı dala commit'ler.
2. **G17'yi dosya gelene kadar durdurmak:** Grup bekler; bulut kredisi ve oturum boşa gider.
3. **Dosyayı elle ya da başka bir kaynaktan üretmek:** ADR-0033'ün kaynak, filtre ve lisans koşullarını bozar.

## Karar

- Bulut oturumu `python scripts/fetch_demo_books.py --out seed/books_openlibrary.json --limit 300` komutunu çalıştırmayı dener; sonuç (başarı ya da ağ hatası) plan G17 kanıtına yazılır.
- Ağ engelliyse `seed/books_openlibrary.json` dala girmez. G17'nin testleri test klasöründeki küçük bir örnek dosyayla (ve testin ürettiği dosyalarla) koşar; dosya yolu testte değiştirilir.
- Gerçek dosya, kullanıcının yerel doğrulamasında aynı komutla çekilir, `_meta` alanı ve kayıt sayısı kontrol edilir ve `feature/seed-load` dalına commit'lenir. Bu adım `docs/STATUS.md`'nin "Sıradaki adım" bölümüne yazılır; PR bu commit gelmeden birleştirilmez.
- `load_seed_data` dosya yoksa ağa çıkmaz ve sessizce tamamen sentetik veri üretmez; hata verir (metin plan §11'de).

## Sonuçlar

- **Olumlu:** Grup ağ engeline takılmadan ilerler; ADR-0033'ün kaynak ve filtre kuralları değişmez; testler ağdan bağımsız kalır.
- **Olumsuz / riskler:**
  - Betiğin gerçek Open Library cevabıyla çalıştığı ancak yerel doğrulamada görülür; bulutta yalnız sahte cevaplarla sınanır.
  - Gerçek dosya gelene kadar dalda demo verisi yüklenemez; bulutta elle doğrulama geçici bir örnek dosyayla yapılır.

## İzlenebilirlik

- **Gereksinim:** FR-29; AC-29. Plan G17, §11 (G17–G18 açılış kararları).
- **Bağlantılı:** ADR-0033, ADR-0048
