import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KiPouCuit.settings")
get_wsgi_application()

from meals.models import MenuItem


MEALS = [

    # ============================
    #      INDIAN (10 ITEMS)
    # ============================
    {
        "cuisine": "indian",
        "name": "Butter Chicken",
        "price": 250.00,
        "description": "Tender chunks of marinated chicken cooked in a rich, creamy tomato-based gravy infused with aromatic spices, butter, and fresh cream. A beloved North Indian classic that's perfectly balanced between sweet and savory.",
        "image_url": "",
    },
    {
        "cuisine": "indian",
        "name": "Chicken Tikka Masala",
        "price": 240.00,
        "description": "Succulent pieces of grilled chicken tikka simmered in a velvety masala sauce made with tomatoes, cream, and a blend of traditional Indian spices. Each bite delivers smoky, tangy, and mildly spiced flavors.",
        "image_url": "",
    },
    {
        "cuisine": "indian",
        "name": "Paneer Butter Masala",
        "price": 200.00,
        "description": "Soft, pillowy cubes of fresh paneer cheese bathed in a luxurious butter-rich tomato sauce with cashew paste, cream, and aromatic spices. A vegetarian favorite that's indulgent and comforting.",
        "image_url": "",
    },
    {
        "cuisine": "indian",
        "name": "Vegetable Biryani",
        "price": 180.00,
        "description": "Fragrant basmati rice layered with fresh seasonal vegetables, caramelized onions, and aromatic spices including saffron, cardamom, and bay leaves. Slow-cooked to perfection for a flavorful vegetarian feast.",
        "image_url": "",
    },
    {
        "cuisine": "indian",
        "name": "Chicken Biryani",
        "price": 220.00,
        "description": "Classic Hyderabad-style aromatic rice dish with tender marinated chicken pieces, fragrant basmati rice, fried onions, and a perfect blend of whole spices. Served with raita and traditionally cooked in the dum style.",
        "image_url": "",
    },
    {
        "cuisine": "indian",
        "name": "Masala Dosa",
        "price": 150.00,
        "description": "Golden, crispy South Indian crepe made from fermented rice and lentil batter, generously filled with a savory mixture of spiced potatoes, onions, and curry leaves. Served with coconut chutney and sambar.",
        "image_url": "",
    },
    {
        "cuisine": "indian",
        "name": "Rogan Josh",
        "price": 260.00,
        "description": "Authentic Kashmiri lamb curry featuring tender meat braised in a fragrant sauce of yogurt, garlic, ginger, and aromatic spices including Kashmiri chilies. The dish is known for its deep red color and rich, complex flavors.",
        "image_url": "",
    },
    {
        "cuisine": "indian",
        "name": "Aloo Paratha",
        "price": 120.00,
        "description": "Wholesome whole wheat flatbread stuffed with a spiced mixture of mashed potatoes, herbs, and aromatic spices, then pan-fried with ghee until golden and crispy. Perfect for breakfast or a light meal.",
        "image_url": "",
    },
    {
        "cuisine": "indian",
        "name": "Chicken Korma",
        "price": 240.00,
        "description": "Delicate and creamy Mughlai curry featuring tender chicken pieces cooked in a mild, aromatic sauce of yogurt, cream, cashews, and fragrant spices. Rich and indulgent without being overwhelmingly spicy.",
        "image_url": "",
    },

    # ============================
    #   MAURITIAN (10 ITEMS)
    # ============================
    {
        "cuisine": "mauritian",
        "name": "Mine Bouille",
        "price": 120.00,
        "description": "Traditional Mauritian comfort food featuring soft boiled noodles served in a flavorful broth, topped with your choice of vegetables, meat, or seafood. A beloved local favorite that's warm and satisfying.",
        "image_url": "",
    },
    {
        "cuisine": "mauritian",
        "name": "Mauritian Fried Rice",
        "price": 140.00,
        "description": "Fragrant wok-tossed rice stir-fried with scrambled eggs, fresh vegetables, soy sauce, and aromatic spices. This Mauritian version has its own unique blend of flavors influenced by Chinese, Indian, and Creole cuisines.",
        "image_url": "",
    },
    {
        "cuisine": "mauritian",
        "name": "Kebab Sandwich",
        "price": 100.00,
        "description": "Mauritian street food classic featuring spiced minced meat patty nestled in warm pita bread with fresh vegetables, chili sauce, and creamy garlic sauce. A perfect handheld meal bursting with local flavors.",
        "image_url": "",
    },
    {
        "cuisine": "mauritian",
        "name": "Biryani",
        "price": 200.00,
        "description": "Mauritian-style spiced rice dish layered with tender meat, potatoes, and aromatic spices including saffron and star anise. Cooked slowly to allow the flavors to meld, creating a unique local interpretation of this classic dish.",
        "image_url": "",
    },
    {
        "cuisine": "mauritian",
        "name": "Sept Cari",
        "price": 250.00,
        "description": "Traditional seven-curry vegetarian feast featuring seven different vegetable curries served together, typically including pumpkin, beans, eggplant, and lentils. A celebration of Mauritian Creole cooking, often enjoyed on special occasions.",
        "image_url": "",
    },
    {
        "cuisine": "mauritian",
        "name": "Boulette Soup",
        "price": 130.00,
        "description": "Comforting clear broth soup filled with tender steamed dumplings made from chayote or other vegetables, often accompanied by fried wonton wrappers. A beloved Sino-Mauritian dish perfect for any time of day.",
        "image_url": "",
    },
    {
        "cuisine": "mauritian",
        "name": "Gateau Piment",
        "price": 30.00,
        "description": "Popular Mauritian snack of crispy fried chili cakes made with yellow split peas (dholl), fresh herbs, and fiery bird's eye chilies. Crunchy on the outside, soft inside, and packed with spicy flavor.",
        "image_url": "",
    },
    {
        "cuisine": "mauritian",
        "name": "Fish Vindaye",
        "price": 180.00,
        "description": "Traditional Mauritian pickled fish dish where fresh fish is fried then cooked in a tangy mustard-based sauce with onions, garlic, ginger, and turmeric. Best enjoyed cold as a flavorful side dish or main course.",
        "image_url": "",
    },
    {
        "cuisine": "mauritian",
        "name": "Rougaille Saucisse",
        "price": 150.00,
        "description": "Hearty Creole tomato-based stew featuring grilled sausages simmered with onions, garlic, ginger, thyme, and chili. A comfort food staple typically served with rice, bringing together bold, rustic flavors.",
        "image_url": "",
    },

    # ============================
    #   ENGLISH (10 ITEMS)
    # ============================
    {
        "cuisine": "english",
        "name": "Fish and Chips",
        "price": 300.00,
        "description": "Classic British favorite featuring flaky white fish coated in a light, crispy beer batter, served with golden thick-cut chips. Accompanied by mushy peas, tartar sauce, and a lemon wedge for the authentic experience.",
        "image_url": "",
    },
    {
        "cuisine": "english",
        "name": "Full English Breakfast",
        "price": 280.00,
        "description": "Hearty traditional breakfast spread including fried eggs, crispy bacon, pork sausages, baked beans, grilled tomatoes, sautéed mushrooms, black pudding, and buttered toast. The perfect way to start your day.",
        "image_url": "",
    },
    {
        "cuisine": "english",
        "name": "Steak and Ale Pie",
        "price": 260.00,
        "description": "Traditional pub favorite with tender chunks of beef slow-cooked in rich ale gravy with onions and mushrooms, all encased in flaky golden pastry. Served piping hot with your choice of sides.",
        "image_url": "",
    },
    {
        "cuisine": "english",
        "name": "Cornish Pasty",
        "price": 180.00,
        "description": "Authentic hand-crimped pastry from Cornwall, filled with chunks of beef, potato, swede, and onion, seasoned with salt and pepper. A satisfying portable meal with a perfect balance of meat and vegetables.",
        "image_url": "",
    },
    {
        "cuisine": "english",
        "name": "Bangers and Mash",
        "price": 220.00,
        "description": "Classic British comfort food featuring juicy pork sausages served on a bed of creamy, buttery mashed potatoes, all smothered in rich onion gravy. Simple, hearty, and deeply satisfying.",
        "image_url": "",
    },
    {
        "cuisine": "english",
        "name": "Sunday Roast",
        "price": 300.00,
        "description": "Traditional Sunday feast with succulent roast beef, crispy roast potatoes, Yorkshire pudding, seasonal vegetables, and lashings of rich gravy. A British institution that brings families together.",
        "image_url": "",
    },
    {
        "cuisine": "english",
        "name": "Chicken Tikka Sandwich",
        "price": 160.00,
        "description": "Modern British sandwich featuring tender chicken marinated in tikka spices, served in fresh bread with crisp lettuce, tomatoes, and cooling yogurt-mint sauce. A fusion favorite from Britain's multicultural food scene.",
        "image_url": "",
    },
    {
        "cuisine": "english",
        "name": "Cottage Pie",
        "price": 240.00,
        "description": "Homestyle dish similar to shepherd's pie but made with savory minced beef instead of lamb, cooked in rich gravy with carrots and peas, topped with fluffy mashed potato and baked until bubbling.",
        "image_url": "",
    },
    {
        "cuisine": "english",
        "name": "Yorkshire Pudding",
        "price": 110.00,
        "description": "Light and airy baked batter pudding with a crispy golden exterior and soft center, traditionally served as part of a roast dinner. Made from a simple batter of eggs, flour, and milk.",
        "image_url": "",
    },

    # ============================
    #   FRENCH (10 ITEMS)
    # ============================
    {
        "cuisine": "french",
        "name": "Beef Bourguignon",
        "price": 320.00,
        "description": "Elegant French stew featuring tender beef braised for hours in full-bodied Burgundy wine with pearl onions, mushrooms, bacon, and aromatic herbs. A rustic yet refined dish that exemplifies French comfort cooking.",
        "image_url": "",
    },
    {
        "cuisine": "french",
        "name": "Ratatouille",
        "price": 180.00,
        "description": "Vibrant Provençal vegetable stew showcasing the best of summer produce including eggplant, zucchini, bell peppers, and tomatoes, slowly cooked with garlic, herbs, and olive oil until perfectly tender.",
        "image_url": "",
    },
    {
        "cuisine": "french",
        "name": "Coq au Vin",
        "price": 290.00,
        "description": "Classic French braised chicken dish where tender chicken pieces are slow-cooked in red wine with mushrooms, pearl onions, bacon, and herbs until the meat falls off the bone. A countryside favorite.",
        "image_url": "",
    },
    {
        "cuisine": "french",
        "name": "Quiche Lorraine",
        "price": 220.00,
        "description": "Savory French tart featuring a buttery pastry crust filled with a silky custard mixture of eggs, cream, crispy bacon, and cheese. Served warm or at room temperature for breakfast, lunch, or light dinner.",
        "image_url": "",
    },
    {
        "cuisine": "french",
        "name": "Nicoise Salad",
        "price": 190.00,
        "description": "Fresh and colorful salad from Nice featuring seared tuna, hard-boiled eggs, green beans, tomatoes, anchovies, and olives on a bed of crisp lettuce, dressed with olive oil and lemon. Light yet satisfying.",
        "image_url": "",
    },
    {
        "cuisine": "french",
        "name": "French Onion Soup",
        "price": 170.00,
        "description": "Deeply flavored soup made with slowly caramelized onions simmered in rich beef broth, topped with toasted bread and melted Gruyère cheese. A warming Parisian bistro classic that's both elegant and comforting.",
        "image_url": "",
    },
    {
        "cuisine": "french",
        "name": "Cassoulet",
        "price": 310.00,
        "description": "Hearty slow-cooked casserole from southern France featuring white beans, duck confit, pork sausage, and herbs, topped with a golden breadcrumb crust. A rich, rustic dish perfect for cold weather.",
        "image_url": "",
    },
    {
        "cuisine": "french",
        "name": "Madeleines",
        "price": 80.00,
        "description": "Delicate shell-shaped French sponge cakes with a distinctive hump, made with butter, eggs, and a hint of lemon. Light, tender, and slightly sweet - perfect for afternoon tea or as a delicate dessert.",
        "image_url": "",
    },
    {
        "cuisine": "french",
        "name": "Crème Brûlée",
        "price": 140.00,
        "description": "Luxurious French dessert featuring smooth, rich vanilla custard topped with a layer of caramelized sugar that cracks dramatically under your spoon. The perfect contrast of creamy and crunchy textures.",
        "image_url": "",
    },

    # ============================
    #   ASIAN (10 ITEMS)
    # ============================
    {
        "cuisine": "asian",
        "name": "Sushi Platter",
        "price": 450.00,
        "description": "Artfully arranged selection of fresh sushi including nigiri, maki rolls, and sashimi featuring premium seafood like salmon, tuna, and shrimp. Served with pickled ginger, wasabi, and soy sauce for an authentic Japanese experience.",
        "image_url": "",
    },
    {
        "cuisine": "asian",
        "name": "Beef Ramen",
        "price": 260.00,
        "description": "Steaming bowl of authentic Japanese noodle soup with rich, savory broth simmered for hours, tender sliced beef, springy ramen noodles, soft-boiled egg, bamboo shoots, and fresh green onions. Comfort in a bowl.",
        "image_url": "",
    },
    {
        "cuisine": "asian",
        "name": "Chicken Teriyaki",
        "price": 220.00,
        "description": "Succulent grilled chicken glazed with sweet and savory teriyaki sauce made from soy sauce, mirin, and sugar. Served with steamed rice and vegetables for a balanced, flavorful Japanese meal.",
        "image_url": "",
    },
    {
        "cuisine": "asian",
        "name": "Beef Bulgogi",
        "price": 280.00,
        "description": "Korean grilled beef marinated in a sweet and savory mixture of soy sauce, sesame oil, garlic, and pear, then grilled to caramelized perfection. Tender, flavorful, and slightly charred at the edges.",
        "image_url": "",
    },
    {
        "cuisine": "asian",
        "name": "Tempura Udon",
        "price": 240.00,
        "description": "Thick, chewy Japanese udon noodles served in a light, flavorful dashi broth, topped with an assortment of crispy, golden tempura-fried vegetables and shrimp. A satisfying combination of textures.",
        "image_url": "",
    },
    {
        "cuisine": "asian",
        "name": "Mapo Tofu",
        "price": 190.00,
        "description": "Fiery Sichuan classic featuring silky soft tofu and minced pork in a spicy, numbing sauce made with fermented bean paste, chili oil, and Sichuan peppercorns. Served over steamed rice to balance the heat.",
        "image_url": "",
    },
    {
        "cuisine": "asian",
        "name": "Fried Rice",
        "price": 150.00,
        "description": "Classic wok-tossed fried rice with scrambled eggs, green peas, carrots, and soy sauce. Each grain is perfectly separated and lightly coated with savory seasonings. Simple yet satisfying comfort food.",
        "image_url": "",
    },
    {
        "cuisine": "asian",
        "name": "Miso Soup",
        "price": 90.00,
        "description": "Traditional Japanese soup made with dashi broth and fermented soybean paste, filled with silky tofu cubes, wakame seaweed, and sliced green onions. Light, warming, and packed with umami flavor.",
        "image_url": "",
    },
    {
        "cuisine": "asian",
        "name": "Spring Rolls",
        "price": 120.00,
        "description": "Crispy golden fried rolls filled with a savory mixture of shredded vegetables, glass noodles, and seasonings, wrapped in thin pastry. Served hot with sweet chili sauce or soy-based dipping sauce.",
        "image_url": "",
    },

    # ============================
    #    THAI (10 ITEMS)
    # ============================
    {
        "cuisine": "thai",
        "name": "Pad Thai",
        "price": 220.00,
        "description": "Thailand's most famous street food dish featuring stir-fried rice noodles with tofu, eggs, bean sprouts, and crushed peanuts in a perfect balance of sweet, sour, and savory tamarind sauce. Garnished with lime and fresh herbs.",
        "image_url": "",
    },
    {
        "cuisine": "thai",
        "name": "Green Curry",
        "price": 240.00,
        "description": "Aromatic Thai curry featuring tender meat or vegetables in a vibrant green coconut milk-based sauce made with fresh green chilies, Thai basil, kaffir lime, and exotic spices. Spicy, creamy, and herbaceous.",
        "image_url": "",
    },
    {
        "cuisine": "thai",
        "name": "Chicken Satay",
        "price": 200.00,
        "description": "Tender marinated chicken skewers grilled over charcoal until slightly charred, served with rich, creamy peanut sauce and a side of refreshing cucumber relish. A perfect appetizer or light meal.",
        "image_url": "",
    },
    {
        "cuisine": "thai",
        "name": "Thai Fried Rice",
        "price": 160.00,
        "description": "Fragrant jasmine rice stir-fried with chicken, eggs, tomatoes, and onions, seasoned with Thai fish sauce and aromatic herbs. Garnished with cucumber slices and a lime wedge for authentic Thai flavors.",
        "image_url": "",
    },
    {
        "cuisine": "thai",
        "name": "Massaman Curry",
        "price": 260.00,
        "description": "Rich, mild Thai curry with Persian influences, featuring tender meat slow-cooked with potatoes, peanuts, and onions in a creamy coconut milk sauce spiced with cardamom, cinnamon, and star anise.",
        "image_url": "",
    },
    {
        "cuisine": "thai",
        "name": "Papaya Salad",
        "price": 150.00,
        "description": "Refreshing and fiery salad made with shredded green papaya, tomatoes, long beans, and peanuts, dressed with a spicy lime-based dressing featuring chilies, garlic, and palm sugar. Known as Som Tam in Thailand.",
        "image_url": "",
    },
    {
        "cuisine": "thai",
        "name": "Thai Basil Chicken",
        "price": 210.00,
        "description": "Quick and flavorful stir-fry featuring ground or sliced chicken cooked with fresh Thai holy basil, chilies, garlic, and fish sauce. Served over jasmine rice with a fried egg on top for the ultimate comfort meal.",
        "image_url": "",
    },
    {
        "cuisine": "thai",
        "name": "Pineapple Fried Rice",
        "price": 190.00,
        "description": "Sweet and savory fried rice cooked with fresh pineapple chunks, cashews, raisins, and curry powder, often served in a hollowed pineapple shell. A beautiful balance of tropical sweetness and aromatic spices.",
        "image_url": "",
    },
    {
        "cuisine": "thai",
        "name": "Red Curry",
        "price": 250.00,
        "description": "Classic Thai curry with a bold red color and medium-high spice level, made with red curry paste, coconut milk, bamboo shoots, bell peppers, and Thai basil. Creamy, spicy, and deeply satisfying.",
        "image_url": "",
    },
]

for meal in MEALS:
    MenuItem.objects.create(
        name=meal["name"],
        price=meal["price"],
        cuisine=meal["cuisine"],
        description=meal["description"],
        image_url=meal["image_url"]
    )