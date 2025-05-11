defmodule EventManagementApplication.Attendee do
  use Ecto.Schema
  import Ecto.Changeset

  schema "attendees" do
    field :name, :string
    field :email, :string
    field :unique_id, :string
    field :qr_code_path, :string
    field :registered, :boolean, default: false
    field :registered_at, :utc_datetime
    field :lunch_collected, :boolean, default: false
    field :lunch_collected_at, :utc_datetime
    field :kit_collected, :boolean, default: false
    field :kit_collected_at, :utc_datetime

    timestamps()
  end

  def changeset(attendee, attrs) do
  attendee
  |> cast(attrs, [:name, :email, :unique_id, :qr_code_path, :registered, :registered_at,
                  :lunch_collected, :lunch_collected_at, :kit_collected, :kit_collected_at])
  |> validate_required([:name, :email])
  |> validate_format(:email, ~r/^[^\s]+@[^\s]+$/, message: "must have the @ sign and no spaces")
  |> unique_constraint(:email)
  |> unique_constraint(:unique_id)
  end
end
