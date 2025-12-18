class Store < ApplicationRecord
  validates :shop_domain, presence: true
  validates :access_token, presence: true
end
