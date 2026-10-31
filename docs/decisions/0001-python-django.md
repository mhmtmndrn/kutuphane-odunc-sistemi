# ADR-0001: Dil ve web framework olarak Python ve Django

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 3, 1. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

Sistem yerel ağdaki tek bir sunucuda çalışacak ve yalnız personel kullanacak. Sunucunun işletim sistemi belli değil, bu yüzden çözüm Windows ve Linux'ta çalışmalı (SRS bölüm 7, açık soru 5). Gereksinimler şunlar:

- Rol ve oturum yönetimi (FR-21, FR-22, FR-27).
- Argon2id ya da bcrypt ile parola saklama (NFR-06).
- Günlük zamanlanmış görevler (FR-18, FR-25, FR-28).
- Code 128 barkodlu PDF etiket (FR-06).
- Kuruş hassasiyetinde para hesabı (NFR-12).
- TDD ve iş kurallarında en az %90 dal kapsamı (NFR-13).

## Değerlendirilen seçenekler

1. **Python + Django** (seçildi): Oturum, rol, oturum süresi, CSRF, migration ve admin paneli hazır. Argon2 hasher yerleşik (argon2-cffi ile). reportlab Code 128 üretebiliyor. Test zinciri pytest, pytest-django ve coverage. Efor en düşük. Eksileri: yerleşik zamanlayıcı yok, hesap kilidi için ek parça gerekiyor, Windows'ta servis için bir sarmalayıcı lazım.
2. **C# + ASP.NET Core:** Runtime'sız tek dosya halinde yayınlanabiliyor. Kilit ve zamanlayıcı yerleşik. Ancak varsayılan hasher PBKDF2 ve NFR-06'yı karşılamıyor; özel hasher gerekirdi.
3. **Java + Spring Boot:** Zamanlayıcı ve bcrypt yerleşik. Bu ölçek için ağır ve şablon kod fazla.
4. **Node/React SPA:** Elendi. İki kod tabanı ve elle kurulan kimlik doğrulama gerektiriyor, buna ihtiyaç duyan bir gereksinim de yok.

## Karar

Uygulama Python ve Django ile yazılır. Sürüm ve ek bağımlılıklar ayrı kararlarda ve faz 4 planında sabitlenir.

**Kapsanan bağımlılıklar** (kullanıcı teyidi, 2026-10-31): Django ekosisteminin standart parçaları olan `pytest`, `pytest-django`, `coverage` ve `argon2-cffi` için ayrı ADR yazılmaz; bunlar bu kararın kapsamındadır. Sürümleri faz 4 planında sabitlenir.

## Sonuçlar

- **Olumlu:** Gerekli altyapının çoğu hazır geldiği için geliştirme hızlı. Ayar ve personel ekranlarında admin paneli kullanılabilir. TDD araçları olgun.
- **Olumsuz / riskler:**
  - Dinamik tip. Testler ve isteğe bağlı mypy ile azaltılır.
  - Zamanlayıcı ADR-0007'de, hesap kilidi ADR-0009'da, Windows servisi ADR-0010'da ayrıca çözüldü.

## İzlenebilirlik

- **Gereksinim:** FR-06, FR-18, FR-21, FR-22, FR-25, FR-27, FR-28; NFR-06, NFR-12, NFR-13
- **Bağlantılı:** ADR-0002, ADR-0003, ADR-0007, ADR-0009, ADR-0010, ADR-0012
