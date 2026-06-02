# Diagram Star Schema ReTrack (Mermaid) — untuk Slide 8

> Render di: editor Markdown yang mendukung Mermaid (VS Code + ekstensi Mermaid),
> GitHub, atau **https://mermaid.live** → ekspor PNG/SVG untuk ditempel ke PPT.

---

## Versi 1 — ER Diagram (RECOMMENDED, paling jelas untuk PPT)

Menampilkan kolom tiap tabel + relasi fakta→dimensi (bentuk bintang).

```mermaid
erDiagram
    dwh_dim_date {
        varchar date_id PK
        date    full_date
        int     day
        int     month
        varchar month_name
        int     quarter
        int     year
        varchar day_of_week
        bool    is_weekend
    }
    dwh_dim_user {
        int     user_id PK
        varchar name
        varchar email
        date    created_at
    }
    dwh_dim_wallet {
        int     wallet_id PK
        varchar name
        varchar type
    }
    dwh_dim_category {
        int     category_id PK
        varchar name
        varchar kind
    }
    dwh_fact_transaction {
        int     fact_id PK
        varchar date_id FK
        int     user_id FK
        int     wallet_id FK
        int     category_id FK
        numeric amount
        varchar kind
        float   usd_rate_at_date
        float   erosi_persen
        datetime etl_loaded_at
    }

    dwh_dim_date     ||--o{ dwh_fact_transaction : "date_id"
    dwh_dim_user     ||--o{ dwh_fact_transaction : "user_id"
    dwh_dim_wallet   ||--o{ dwh_fact_transaction : "wallet_id"
    dwh_dim_category ||--o{ dwh_fact_transaction : "category_id"
```

---

## Versi 2 — Flowchart bentuk bintang (lebih visual "star")

Fakta di tengah, 4 dimensi mengelilingi → terlihat seperti bintang.

```mermaid
flowchart TB
    DATE[("⬩ dim_date<br/>date_id PK<br/>month, quarter, year<br/>day_of_week, is_weekend")]
    CAT[("⬩ dim_category<br/>category_id PK<br/>name, kind")]
    FACT{{"★ fact_transaction<br/>fact_id PK<br/>amount · kind<br/>erosi_persen<br/>usd_rate_at_date"}}
    WAL[("⬩ dim_wallet<br/>wallet_id PK<br/>name, type")]
    USER[("⬩ dim_user<br/>user_id PK<br/>name, email")]

    DATE --- FACT
    CAT  --- FACT
    FACT --- WAL
    USER --- FACT

    classDef fact fill:#F76B8A,stroke:#c44,color:#fff,font-weight:bold;
    classDef dim  fill:#EAF6F6,stroke:#66BFBF,color:#0a4a4a;
    class FACT fact;
    class DATE,CAT,WAL,USER dim;
```

> Warna mengikuti palet ReTrack: fakta = pink `#F76B8A` (aksen), dimensi = teal muda `#EAF6F6` (brand).

---

## Versi 3 — Ringkas (tanpa kolom, untuk slide minimalis)

```mermaid
flowchart LR
    DATE([dim_date]) --> FACT
    CAT([dim_category]) --> FACT
    USER([dim_user]) --> FACT
    WAL([dim_wallet]) --> FACT
    FACT{{fact_transaction}}

    classDef fact fill:#F76B8A,stroke:#c44,color:#fff,font-weight:bold;
    classDef dim fill:#EAF6F6,stroke:#66BFBF,color:#0a4a4a;
    class FACT fact;
    class DATE,CAT,USER,WAL dim;
```

---

### Cara ekspor ke gambar untuk PPT
1. Buka **https://mermaid.live**
2. Tempel salah satu blok kode di atas (tanpa baris ```mermaid)
3. Klik **Actions → PNG/SVG** → tempel ke slide 8.

Saran: **Versi 1 (ER)** untuk menjelaskan detail kolom, atau **Versi 2** bila ingin bentuk bintang yang jelas secara visual.
