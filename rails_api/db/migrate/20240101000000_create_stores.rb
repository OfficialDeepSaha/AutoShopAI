class CreateStores < ActiveRecord::Migration[7.1]
  def change
    create_table :stores do |t|
      t.string :shop_domain, null: false
      t.string :access_token, null: false
      t.timestamps
    end
    add_index :stores, :shop_domain, unique: true
  end
end
