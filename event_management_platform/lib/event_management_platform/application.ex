defmodule EventManagementPlatform.Application do
  # See https://hexdocs.pm/elixir/Application.html
  # for more information on OTP Applications
  @moduledoc false

  use Application

  @impl true
  def start(_type, _args) do
    children = [
      EventManagementPlatformWeb.Telemetry,
      EventManagementPlatform.Repo,
      {DNSCluster, query: Application.get_env(:event_management_platform, :dns_cluster_query) || :ignore},
      {Phoenix.PubSub, name: EventManagementPlatform.PubSub},
      # Start the Finch HTTP client for sending emails
      {Finch, name: EventManagementPlatform.Finch},
      # Start a worker by calling: EventManagementPlatform.Worker.start_link(arg)
      # {EventManagementPlatform.Worker, arg},
      # Start to serve requests, typically the last entry
      EventManagementPlatformWeb.Endpoint
    ]

    # See https://hexdocs.pm/elixir/Supervisor.html
    # for other strategies and supported options
    opts = [strategy: :one_for_one, name: EventManagementPlatform.Supervisor]
    Supervisor.start_link(children, opts)
  end

  # Tell Phoenix to update the endpoint configuration
  # whenever the application is updated.
  @impl true
  def config_change(changed, _new, removed) do
    EventManagementPlatformWeb.Endpoint.config_change(changed, removed)
    :ok
  end
end
