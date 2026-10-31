# ADR-0050: Kilitliyken yapılan denemeler 15 dakikalık kilit süresini uzatmaz

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Kullanıcı, 2026-10-31 faz 5 oturumunda soru penceresinden seçti.

## Bağlam

- ADR-0009: `AXES_FAILURE_LIMIT = 5`, `AXES_COOLOFF_TIME = 15 dakika`.
- django-axes'te `AXES_RESET_COOL_OFF_ON_FAILURE_DURING_LOCKOUT` varsayılan olarak `True`'dur. Bu durumda kilitliyken yapılan her başarısız deneme bekleme süresini baştan başlatır.
- Kilit mesajı "15 dakika sonra yeniden deneyin." diyor (ADR-0049). TC-08'in 14:59 ve 15:01 sınırları, sürenin neye göre ölçüldüğüne bağlı.

## Değerlendirilen seçenekler

1. **`False`, süre uzamaz** (seçildi): Kilit, kilidi tetikleyen 5. hatalı denemeden 15 dakika sonra açılır ve mesaj doğru kalır. Kilit süresince bütün denemeler zaten reddedildiği için kaba kuvvet koruması zayıflamaz.
2. **`True`, axes varsayılanı:** Israrcı saldırgana karşı biraz daha serttir. Ancak denemeye devam eden personel kilitte kalır, mesaj yanıltıcı olur ve yöneticinin elle kilit kaldırma ihtiyacı artar.

## Karar

- `AXES_RESET_COOL_OFF_ON_FAILURE_DURING_LOCKOUT = False`.
- 15 dakikalık süre, kilidi tetikleyen 5. hatalı denemenin zamanından ölçülür. Kilit süresince yapılan denemeler (doğru parolayla da olsa) reddedilir (ADR-0049) ve süreyi değiştirmez.

## Sonuçlar

- **Olumlu:** Davranış öngörülebilir; mesaj, test ve ayar aynı şeyi söyler.
- **Olumsuz / riskler:** Saldırgan her 15 dakikada en fazla 5 deneme yapabilir. LAN içi ve yalnız personel kullanımında bu kabul edilebilir (ADR-0009'daki risk değerlendirmesiyle aynı çerçeve).

## İzlenebilirlik

- **Gereksinim:** FR-27, AC-27. Plan G02; TC-08.
- **Bağlantılı:** ADR-0009, ADR-0049
