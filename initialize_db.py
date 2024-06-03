from user_operations import add_user, authenticate_user

names_list = [
('john_doe', 'john@example.com', 'hashed_password_1', 'John', 'Doe', 'user'),
('jane_smith', 'jane@example.com', 'hashed_password_2', 'Jane', 'Smith', 'admin'),
('mike_jones', 'mike@example.com', 'hashed_password_3', 'Mike', 'Jones', 'user'),
('anna_brown', 'anna@example.com', 'hashed_password_4', 'Anna', 'Brown', 'user'),
('chris_white', 'chris@example.com', 'hashed_password_5', 'Chris', 'White', 'user'),
('kate_green', 'kate@example.com', 'hashed_password_6', 'Kate', 'Green', 'user'),
('tom_clark', 'tom@example.com', 'hashed_password_7', 'Tom', 'Clark', 'user'),
('lucy_adams', 'lucy@example.com', 'hashed_password_8', 'Lucy', 'Adams', 'user'),
('david_lee', 'david@example.com', 'hashed_password_9', 'David', 'Lee', 'user'),
('sara_hall', 'sara@example.com', 'hashed_password_10', 'Sara', 'Hall', 'admin')]

recipe_list = [
    ('Spaghetti Bolognese', 'Main Course', 'A classic Italian pasta dish', '1. Cook the pasta. 2. Prepare the sauce. 3. Mix and serve.', 600, 1),
('Chicken Caesar Salad', 'Salad', 'A healthy Caesar salad with grilled chicken', '1. Grill the chicken. 2. Prepare the salad. 3. Mix and serve.', 350, 2),
('Chocolate Cake', 'Dessert', 'A rich and moist chocolate cake', '1. Prepare the batter. 2. Bake the cake. 3. Let it cool and serve.', 450, 1),
('Vegetable Stir Fry', 'Main Course', 'A quick and easy vegetable stir fry', '1. Prepare the vegetables. 2. Stir fry the vegetables. 3. Serve with rice.', 300, 3),
('Pancakes', 'Breakfast', 'Fluffy pancakes perfect for breakfast', '1. Prepare the batter. 2. Cook the pancakes. 3. Serve with syrup.', 400, 1),
('Beef Tacos', 'Main Course', 'Spicy beef tacos with salsa', '1. Prepare the beef. 2. Warm the tortillas. 3. Assemble the tacos and serve.', 500, 4),
('Lemon Tart', 'Dessert', 'A zesty lemon tart with a crispy crust', '1. Prepare the crust. 2. Make the lemon filling. 3. Bake and serve.', 350, 5),
('Minestrone Soup', 'Appetizer', 'A hearty vegetable and pasta soup', '1. Prepare the vegetables. 2. Cook the soup. 3. Serve hot.', 200, 6),
('French Toast', 'Breakfast', 'Classic French toast with maple syrup', '1. Prepare the egg mixture. 2. Cook the bread slices. 3. Serve with syrup.', 450, 7),
('Greek Salad', 'Salad', 'A refreshing salad with feta cheese and olives', '1. Prepare the vegetables. 2. Mix the dressing. 3. Toss and serve.', 250, 8),
('Grilled Cheese Sandwich', 'Snack', 'A simple and delicious grilled cheese sandwich', '1. Butter the bread. 2. Add cheese. 3. Grill until golden brown.', 350, 9),
('Apple Pie', 'Dessert', 'A classic apple pie with a flaky crust', '1. Prepare the crust. 2. Make the apple filling. 3. Bake and serve.', 400, 10),
('Roast Chicken', 'Main Course', 'Juicy roast chicken with herbs', '1. Prepare the chicken. 2. Roast in the oven. 3. Serve with vegetables.', 600, 3),
('Fish and Chips', 'Main Course', 'Crispy fish with golden fries', '1. Prepare the fish. 2. Fry the fish and potatoes. 3. Serve with tartar sauce.', 700, 4),
('Caesar Salad', 'Salad', 'Classic Caesar salad with homemade dressing', '1. Prepare the dressing. 2. Toss the salad. 3. Serve with croutons.', 300, 5),
('Pumpkin Soup', 'Appetizer', 'Creamy pumpkin soup with a hint of spice', '1. Prepare the pumpkin. 2. Cook the soup. 3. Serve hot.', 150, 6),
('Scrambled Eggs', 'Breakfast', 'Fluffy scrambled eggs', '1. Beat the eggs. 2. Cook in a pan. 3. Serve hot.', 250, 7),
('Caprese Salad', 'Salad', 'Fresh salad with tomatoes, mozzarella, and basil', '1. Slice the tomatoes and cheese. 2. Arrange on a plate. 3. Drizzle with olive oil and serve.', 200, 8),
('Banana Bread', 'Dessert', 'Moist banana bread with walnuts', '1. Prepare the batter. 2. Bake in the oven. 3. Let it cool and serve.', 350, 9),
('Chicken Noodle Soup', 'Main Course', 'Comforting chicken noodle soup', '1. Prepare the broth. 2. Add chicken and noodles. 3. Serve hot.', 300, 10)
]

def initialize():
    for username, email, password, first, last, role in names_list:

        if (role != 'user'):
            add_user(first, last, email, username, password, role)
        else:
            add_user(first, last, email, username, password)

    user1 = authenticate_user('sara_hall', 'hashed_password_10')
    for title, type, description, instruction, calory, _ in recipe_list:
        user1.add_recipe(title, type, description, instruction, calory)