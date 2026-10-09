from datetime import datetime

import aiosqlite

from bot.config import DATA_DIR, DB_PATH

DEFAULT_CATEGORIES = ["Еда", "Транспорт", "Развлечения", "Здоровье", "Одежда", "Другое"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    UNIQUE(user_id, name)
);

CREATE TABLE IF NOT EXISTS operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('expense', 'income')),
    amount INTEGER NOT NULL,
    category TEXT,
    comment TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ops_user_date ON operations(user_id, created_at);
"""


async def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()


async def ensure_default_categories(user_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT COUNT(*) FROM categories WHERE user_id = ?", (user_id,)
        )
        count = (await cur.fetchone())[0]
        if count == 0:
            await db.executemany(
                "INSERT INTO categories (user_id, name) VALUES (?, ?)",
                [(user_id, name) for name in DEFAULT_CATEGORIES],
            )
            await db.commit()


async def get_categories(user_id: int) -> list[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT name FROM categories WHERE user_id = ? ORDER BY id", (user_id,)
        )
        rows = await cur.fetchall()
    return [row[0] for row in rows]


async def add_category(user_id: int, name: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT OR IGNORE INTO categories (user_id, name) VALUES (?, ?)",
            (user_id, name),
        )
        await db.commit()
        return cur.rowcount > 0


async def rename_category(user_id: int, old_name: str, new_name: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            cur = await db.execute(
                "UPDATE categories SET name = ? WHERE user_id = ? AND name = ?",
                (new_name, user_id, old_name),
            )
            if cur.rowcount == 0:
                return False
            await db.execute(
                "UPDATE operations SET category = ? WHERE user_id = ? AND category = ?",
                (new_name, user_id, old_name),
            )
            await db.commit()
        except aiosqlite.IntegrityError:
            return False
    return True


async def delete_category(user_id: int, name: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "DELETE FROM categories WHERE user_id = ? AND name = ?",
            (user_id, name),
        )
        await db.commit()
        return cur.rowcount > 0


async def add_operation(
    user_id: int,
    op_type: str,
    amount: int,
    category: str | None = None,
    comment: str | None = None,
) -> int:
    created_at = datetime.now().isoformat(timespec="seconds")
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO operations (user_id, type, amount, category, comment, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, op_type, amount, category, comment, created_at),
        )
        await db.commit()
        return cur.lastrowid


async def get_history(user_id: int, limit: int = 10) -> list[tuple]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id, type, amount, category, comment, created_at"
            " FROM operations WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        )
        return await cur.fetchall()


async def delete_last_operation(user_id: int) -> tuple | None:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id, type, amount, category, comment, created_at"
            " FROM operations WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,),
        )
        row = await cur.fetchone()
        if row is None:
            return None
        await db.execute("DELETE FROM operations WHERE id = ?", (row[0],))
        await db.commit()
    return row


async def delete_operation(user_id: int, op_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "DELETE FROM operations WHERE id = ? AND user_id = ?",
            (op_id, user_id),
        )
        await db.commit()
        return cur.rowcount > 0


async def get_month_stats(user_id: int, year: int, month: int) -> dict:
    pattern = f"{year:04d}-{month:02d}%"
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM operations"
            " WHERE user_id = ? AND type = 'expense' AND created_at LIKE ?",
            (user_id, pattern),
        )
        expense = (await cur.fetchone())[0]

        cur = await db.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM operations"
            " WHERE user_id = ? AND type = 'income' AND created_at LIKE ?",
            (user_id, pattern),
        )
        income = (await cur.fetchone())[0]

        cur = await db.execute(
            "SELECT COALESCE(category, 'Другое'), SUM(amount) FROM operations"
            " WHERE user_id = ? AND type = 'expense' AND created_at LIKE ?"
            " GROUP BY category ORDER BY SUM(amount) DESC",
            (user_id, pattern),
        )
        by_category = await cur.fetchall()

    return {"expense": expense, "income": income, "by_category": by_category}
