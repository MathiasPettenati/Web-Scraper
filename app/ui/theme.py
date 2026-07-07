from __future__ import annotations

from nicegui import ui


def apply_theme() -> None:
    ui.add_head_html(
        """
        <meta name="viewport" content="width=device-width, initial-scale=1">
        """
    )
    ui.add_css(
        """
        :root {
          --bg: #fff1d6;
          --surface: #fff7e8;
          --surface-2: #ffe0b8;
          --ink: #3b071f;
          --muted: #8a3d20;
          --line: #ff9f1c;
          --accent: #ff2da8;
          --accent-2: #ff7a18;
          --warn: #ff8a00;
          --danger: #c7277a;
        }
        body.body--dark {
          --bg: #24001a;
          --surface: #3b0628;
          --surface-2: #270016;
          --ink: #fff7ed;
          --muted: #ffd6a5;
          --line: #ff7a18;
          --accent: #ff2da8;
          --accent-2: #ff9f1c;
          --warn: #ffb347;
          --danger: #ff4fa3;
        }
        *, .q-btn, .q-card, .q-field__control, .q-menu, .q-dialog__inner > div {
          border-radius: 0 !important;
        }
        body {
          background: linear-gradient(135deg, var(--bg), #a0006d 48%, #ff6a00);
          color: var(--ink);
          font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          letter-spacing: 0;
        }
        .app-shell {
          max-width: 1440px;
          margin: 0 auto;
          padding: 22px;
        }
        .topbar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 16px;
          padding: 6px 0 18px;
          border-bottom: 1px solid var(--line);
        }
        .brand-lockup {
          display: flex;
          align-items: center;
          gap: 12px;
          min-width: 220px;
        }
        .brand-mark {
          width: 36px;
          height: 36px;
          border-radius: 0;
          background: linear-gradient(135deg, var(--accent), var(--accent-2));
        }
        .brand-title {
          font-weight: 800;
          font-size: 1.35rem;
          line-height: 1.1;
        }
        .nav-row {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          justify-content: flex-end;
          gap: 8px;
        }
        .content-grid {
          display: grid;
          grid-template-columns: minmax(0, 1.6fr) minmax(300px, 0.8fr);
          gap: 20px;
          margin-top: 22px;
        }
        .surface {
          background: var(--surface);
          border: 1px solid var(--line);
          border-radius: 0;
          box-shadow: 0 16px 38px rgba(17, 24, 39, 0.06);
        }
        .section-pad {
          padding: 20px;
        }
        .section-title {
          font-size: 1.05rem;
          font-weight: 800;
          margin-bottom: 12px;
        }
        .form-grid {
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 12px;
        }
        .form-grid .wide { grid-column: span 2; }
        .form-grid .full { grid-column: 1 / -1; }
        .toggle-grid {
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 10px;
        }
        .results-layout {
          display: grid;
          grid-template-columns: 290px minmax(0, 1fr);
          gap: 18px;
          margin-top: 20px;
        }
        .results-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: 16px;
        }
        .results-list {
          display: grid;
          grid-template-columns: 1fr;
          gap: 12px;
        }
        .product-card {
          overflow: hidden;
          background: var(--surface);
          border: 1px solid var(--line);
          border-radius: 0;
          min-height: 100%;
        }
        .product-image {
          width: 100%;
          aspect-ratio: 1 / 1;
          object-fit: contain;
          background: var(--surface-2);
        }
        .product-body {
          padding: 14px;
          display: grid;
          gap: 10px;
        }
        .product-title {
          font-weight: 800;
          line-height: 1.25;
        }
        .muted {
          color: var(--muted);
        }
        .score-row, .price-row, .pill-row {
          display: flex;
          align-items: center;
          flex-wrap: wrap;
          gap: 8px;
        }
        .pill {
          border: 1px solid var(--line);
          border-radius: 0;
          padding: 3px 8px;
          font-size: 0.78rem;
          color: var(--muted);
          background: var(--surface-2);
        }
        .score {
          font-weight: 800;
          color: var(--accent);
        }
        .price-main {
          font-weight: 900;
          font-size: 1.2rem;
        }
        .price-old {
          color: var(--muted);
          text-decoration: line-through;
        }
        .empty-state {
          border: 1px dashed var(--line);
          border-radius: 0;
          padding: 28px;
          color: var(--muted);
          background: var(--surface);
        }
        .skeleton {
          height: 96px;
          border-radius: 0;
          background: linear-gradient(90deg, var(--surface-2), var(--surface), var(--surface-2));
          background-size: 200% 100%;
          animation: shimmer 1.4s infinite;
        }
        @keyframes shimmer { to { background-position-x: -200%; } }
        @media (max-width: 980px) {
          .content-grid, .results-layout {
            grid-template-columns: 1fr;
          }
          .form-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
          }
          .toggle-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
          }
        }
        @media (max-width: 640px) {
          .app-shell {
            padding: 14px;
          }
          .topbar {
            align-items: flex-start;
            flex-direction: column;
          }
          .form-grid {
            grid-template-columns: 1fr;
          }
          .form-grid .wide {
            grid-column: span 1;
          }
          .toggle-grid {
            grid-template-columns: 1fr;
          }
        }
        """
    )
