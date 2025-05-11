defmodule EventManagementPlatformWeb.CsvUploadController do
  use EventManagementPlatformWeb, :controller
  alias EventManagementPlatformWeb.Importer

  def new(conn, _params) do
    render(conn, "new.html")
  end

  def create(conn, %{"upload" => %{"csv" => csv_upload}}) do
    temp_path = csv_upload.path

    case Importer.import_attendees(temp_path) do
      {count, _} when count > 0 ->
        conn
        |> put_flash(:info, "Successfully imported #{count} attendees")
        |> redirect(to: Routes.admin_dashboard_path(conn, :index))

      {0, _} ->
        conn
        |> put_flash(:error, "No new attendees were imported")
        |> render("new.html")
    end
  end
end
