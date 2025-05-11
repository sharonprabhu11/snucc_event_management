
defmodule EventManagementPlatform.IdGenerator do
  @qr_dir "priv/generated_ids"

  def generate_unique_id do
    UUID.uuid4() |> String.slice(0, 8) |> String.upcase()
  end

  def generate_qr_code(unique_id) do

    File.mkdir_p!(@qr_dir)

    filename = "#{unique_id}.png"
    path = Path.join(@qr_dir, filename)

    unique_id
    |> QRCode.create()
    |> QRCode.render()
    |> then(fn qr_code -> File.write!(path, qr_code) end)

    "/generated_ids/#{filename}"
  end
end
