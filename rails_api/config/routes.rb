Rails.application.routes.draw do
  namespace :shopify do
    get 'oauth/install'
    get 'oauth/callback'
  end

  namespace :api do
    namespace :v1 do
      post 'questions', to: 'questions#create'
    end
  end
end
