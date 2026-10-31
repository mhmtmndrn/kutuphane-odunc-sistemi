# ADR-0026: Raftaki nüsha bedelsiz olarak kayıp, hasarlı ya da kayıttan düşmüş işaretlenebilir (FR-39)

- **Durum:** Kabul edildi (2026-10-31)
- **Kaynak:** Faz 4, 1. tur. Kullanıcı soru penceresinden seçti.

## Bağlam

Nüsha durum modelinde (architecture §5.1) yalnız ödünçteki bir nüsha kayıp ya da hasarlı işaretlenebiliyordu (FR-15). Envanter sayımında raftan kaybolan, rafta hasar gören ya da ayıklanan bir nüsha ise sistemde "Rafta" görünmeye devam ediyordu. SRS bu durumu kapsamıyordu.

## Değerlendirilen seçenekler

1. **Bedelsiz işaretleme** (seçildi): Raftaki nüsha kayıp, hasarlı ya da kayıttan düşmüş işaretlenebilir; kayıp nüsha da kayıttan düşülebilir. Bu geçişlerde üye ve bedel yoktur. Envanter gerçeğini yansıtır; maliyeti 4 geçiş ve bunların testleri.
2. **Yalnız ayıklama:** Yalnız Rafta → Kayıttan düşmüş geçişi eklenir. Raftan kaybolan nüsha "Rafta" görünmeye devam eder.
3. **Kapsam dışı:** SRS'e Won't olarak yazılır.

## Karar

- Yeni FR-39 (Should). Yalnız yönetici şu geçişleri yapar: Rafta → Kayıp, Rafta → Hasarlı, Rafta → Kayıttan düşmüş, Kayıp → Kayıttan düşmüş.
- Bu geçişlerde ödünç, borç kaydı ya da bedel oluşmaz. Her geçiş, isteğe bağlı bir notla birlikte denetim kaydına yazılır (FR-26).
- Var olan geçişler aynen kalır: Kayıp → Rafta (bulundu), Hasarlı → Rafta (onarıldı), Hasarlı → Kayıttan düşmüş. Bulunan nüshanın bağlı bir bedel kalemi yoksa iptal adımı atlanır.
- Servis: `circulation.services.mark_shelf_copy(actor, copy, new_status, note) -> Copy`. Diyagram dışındaki her geçiş `InvalidTransition` hatasıyla reddedilir.

## Sonuçlar

- **Olumlu:** Envanter farkları sistemde izlenir; kayıttan düşmüş nüsha ödünç verilemez.
- **Olumsuz / riskler:** `mark_found` hem bedel kalemi olan hem olmayan kayıp nüshayı ele almalı ve iki dal da test edilmeli.

## İzlenebilirlik

- **Gereksinim:** FR-05, FR-16, FR-26, FR-39; AC-32
- **Bağlantılı:** ADR-0020
