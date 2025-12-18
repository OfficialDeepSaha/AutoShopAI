class Api::V1::QuestionsController < ApplicationController
  def create
    store = Store.find_by(shop_domain: params[:store_id])
    return render json: { error: 'Store not found' }, status: 404 unless store

    response = HTTParty.post(
      ENV['AI_SERVICE_URL'] + '/ask',
      headers: { 'Content-Type' => 'application/json' },
      body: {
        shop_domain: store.shop_domain,
        access_token: store.access_token,
        question: params[:question]
      }.to_json
    )

    render json: response.parsed_response
  end
end
