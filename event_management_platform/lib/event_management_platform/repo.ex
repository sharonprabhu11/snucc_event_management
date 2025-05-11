defmodule EventManagementPlatform.Repo do
  use Ecto.Repo,
    otp_app: :event_management_platform,
    adapter: Ecto.Adapters.Postgres
end
