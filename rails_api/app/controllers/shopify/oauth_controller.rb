class Shopify::OauthController < ApplicationController
  def install
    shop = params[:shop]
    scopes = 'read_orders,read_products,read_inventory,read_reports,read_analytics,write_products,write_orders,write_customers,write_inventory'
    redirect_to "https://#{shop}/admin/oauth/authorize?client_id=#{ENV['SHOPIFY_API_KEY']}&scope=#{scopes}&redirect_uri=#{callback_url}"
  end

  def callback
    response = HTTParty.post(
      "https://#{params[:shop]}/admin/oauth/access_token",
      body: {
        client_id: ENV['SHOPIFY_API_KEY'],
        client_secret: ENV['SHOPIFY_API_SECRET'],
        code: params[:code]
      }
    )

    Store.upsert({
      shop_domain: params[:shop],
      access_token: response['access_token'],
      created_at: Time.now,
      updated_at: Time.now
    }, unique_by: :shop_domain)

    render json: { status: 'connected' }
  end

  private

  def callback_url
    "#{request.base_url}/shopify/oauth/callback"
  end
end
