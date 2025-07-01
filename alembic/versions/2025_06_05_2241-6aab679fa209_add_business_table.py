"""Add Business table

Revision ID: 6aab679fa209
Revises: 82c123a2de67
Create Date: 2025-06-05 22:41:51.722773

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "6aab679fa209"
down_revision: Union[str, None] = "82c123a2de67"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # === Create new table ===
    op.create_table(
        "business",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("google_user_id", sa.String(), nullable=True),
        sa.Column("access_token", sa.String(), nullable=True),
        sa.Column("refresh_token", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # === Rename tables for consistency ===
    op.rename_table("stylists", "employees")
    op.rename_table("stylist_services", "employee_services")

    # === Add business_id to employees and set foreign key ===
    op.add_column("employees", sa.Column("business_id", sa.Integer(), nullable=False))
    op.create_foreign_key(
        "employees_business_id_fkey",
        "employees",
        "business",
        ["business_id"],
        ["id"],
    )

    # === Update appointments: rename column and update foreign key ===
    op.drop_constraint(
        "appointments_stylist_id_fkey",
        "appointments",
        type_="foreignkey",
    )
    op.alter_column("appointments", "stylist_id", new_column_name="employee_id")
    op.create_foreign_key(
        "appointments_employee_id_fkey",
        "appointments",
        "employees",
        ["employee_id"],
        ["id"],
    )

    # === Update work_schedules: rename column and update foreign key ===
    op.drop_constraint(
        "work_schedules_stylist_id_fkey",
        "work_schedules",
        type_="foreignkey",
    )
    op.alter_column("work_schedules", "stylist_id", new_column_name="employee_id")
    op.create_foreign_key(
        "work_schedules_employee_id_fkey",
        "work_schedules",
        "employees",
        ["employee_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    # ### Reverse foreign key changes ###
    op.drop_constraint(
        "work_schedules_employee_id_fkey",
        "work_schedules",
        type_="foreignkey",
    )
    op.alter_column("work_schedules", "employee_id", new_column_name="stylist_id")
    op.create_foreign_key(
        "work_schedules_stylist_id_fkey",
        "work_schedules",
        "stylists",
        ["stylist_id"],
        ["id"],
    )

    op.drop_constraint(
        "appointments_employee_id_fkey",
        "appointments",
        type_="foreignkey",
    )
    op.alter_column("appointments", "employee_id", new_column_name="stylist_id")
    op.create_foreign_key(
        "appointments_stylist_id_fkey",
        "appointments",
        "stylists",
        ["stylist_id"],
        ["id"],
    )

    # ### Reverse employee/business relationship ###
    op.drop_constraint("employees_business_id_fkey", "employees", type_="foreignkey")
    op.drop_column("employees", "business_id")

    # ### Rename tables back ###
    op.rename_table("employees", "stylists")
    op.rename_table("employee_services", "stylist_services")

    # ### Drop business table ###
    op.drop_table("business")
