# This file should contain all the record creation needed to seed the database with its default values.
# The data can then be loaded with the bin/rails db:seed command (or created alongside the database with db:setup).

puts "Seeding database..."

# Clear existing stores to avoid duplicates if re-run
Store.destroy_all

# Create the specific store from user credentials
Store.create!(
  shop_domain: 'auto-shopai.myshopify.com',
  access_token: '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'
)

puts "Success! Store 'auto-shopai.myshopify.com' has been seeded."
