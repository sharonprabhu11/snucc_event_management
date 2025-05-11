defmodule EventMangementPlatform.CsvImporter do
  alias NimbleCSV.RFC4180, as: CSV
  alias EventManagementPlatform.Repo
  alias EventMangementPlatform.Attendee
  alias EventMangementPlatform.IdGenerator

  def import_attendees(csv_path) do
    csv_path
    |> File.stream!()
    |> CSV.parse_stream()
    |> Stream.map(fn [name, email | _rest] = row ->
      unique_id = IdGenerator.generate_unique_id()
      qr_path = IdGenerator.generate_qr_code(unique_id)

      %{
        name: name,
        email: email,
        unique_id: unique_id,
        qr_code_path: qr_path
      }
    end)
    |> Enum.to_list()
    |> insert_attendees()
  end

  defp insert_attendees(attendees) do
    Repo.insert_all(Attendee, attendees, on_conflict: :nothing)
  end
end
