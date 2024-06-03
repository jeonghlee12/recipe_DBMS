TRUNCATE TABLE recipe.Bookmark RESTART IDENTITY CASCADE;
TRUNCATE TABLE recipe.Rating RESTART IDENTITY CASCADE;
TRUNCATE TABLE recipe.IngredientEditQueue RESTART IDENTITY CASCADE;
TRUNCATE TABLE recipe.RecipeEditQueue RESTART IDENTITY CASCADE;
TRUNCATE TABLE recipe.Recipe_Ingredients RESTART IDENTITY CASCADE;
TRUNCATE TABLE recipe.Ingredients RESTART IDENTITY CASCADE;
TRUNCATE TABLE recipe.Recipes RESTART IDENTITY CASCADE;
TRUNCATE TABLE recipe.Users RESTART IDENTITY CASCADE;

-- Insert Sample Data
-- Users
INSERT INTO recipe.Users (username, email, password_hash, firstname, lastname, role)
VALUES 
('john_doe', 'john@example.com', 'hashed_password_1', 'John', 'Doe', 'user'),
('jane_smith', 'jane@example.com', 'hashed_password_2', 'Jane', 'Smith', 'admin'),
('mike_jones', 'mike@example.com', 'hashed_password_3', 'Mike', 'Jones', 'user'),
('anna_brown', 'anna@example.com', 'hashed_password_4', 'Anna', 'Brown', 'user'),
('chris_white', 'chris@example.com', 'hashed_password_5', 'Chris', 'White', 'user'),
('kate_green', 'kate@example.com', 'hashed_password_6', 'Kate', 'Green', 'user'),
('tom_clark', 'tom@example.com', 'hashed_password_7', 'Tom', 'Clark', 'user'),
('lucy_adams', 'lucy@example.com', 'hashed_password_8', 'Lucy', 'Adams', 'user'),
('david_lee', 'david@example.com', 'hashed_password_9', 'David', 'Lee', 'user'),
('sara_hall', 'sara@example.com', 'hashed_password_10', 'Sara', 'Hall', 'admin');

-- Recipes
INSERT INTO recipe.Recipes (title, type, description, instructions, calory, creatorID, lastUpdatorID, avgRating, beingEdited)
VALUES
('Spaghetti Bolognese', 'Main Course', 'A classic Italian pasta dish', '1. Cook the pasta. 2. Prepare the sauce. 3. Mix and serve.', 600, 1, 2, 4.5, FALSE),
('Chicken Caesar Salad', 'Salad', 'A healthy Caesar salad with grilled chicken', '1. Grill the chicken. 2. Prepare the salad. 3. Mix and serve.', 350, 2, 1, 4.7, FALSE),
('Chocolate Cake', 'Dessert', 'A rich and moist chocolate cake', '1. Prepare the batter. 2. Bake the cake. 3. Let it cool and serve.', 450, 1, 3, 4.8, FALSE),
('Vegetable Stir Fry', 'Main Course', 'A quick and easy vegetable stir fry', '1. Prepare the vegetables. 2. Stir fry the vegetables. 3. Serve with rice.', 300, 3, 4, 4.2, FALSE),
('Pancakes', 'Breakfast', 'Fluffy pancakes perfect for breakfast', '1. Prepare the batter. 2. Cook the pancakes. 3. Serve with syrup.', 400, 1, 2, 4.6, FALSE),
('Beef Tacos', 'Main Course', 'Spicy beef tacos with salsa', '1. Prepare the beef. 2. Warm the tortillas. 3. Assemble the tacos and serve.', 500, 4, 5, 4.3, FALSE),
('Lemon Tart', 'Dessert', 'A zesty lemon tart with a crispy crust', '1. Prepare the crust. 2. Make the lemon filling. 3. Bake and serve.', 350, 5, 6, 4.9, FALSE),
('Minestrone Soup', 'Appetizer', 'A hearty vegetable and pasta soup', '1. Prepare the vegetables. 2. Cook the soup. 3. Serve hot.', 200, 6, 7, 4.1, FALSE),
('French Toast', 'Breakfast', 'Classic French toast with maple syrup', '1. Prepare the egg mixture. 2. Cook the bread slices. 3. Serve with syrup.', 450, 7, 8, 4.7, FALSE),
('Greek Salad', 'Salad', 'A refreshing salad with feta cheese and olives', '1. Prepare the vegetables. 2. Mix the dressing. 3. Toss and serve.', 250, 8, 9, 4.5, FALSE);

-- Ingredients
INSERT INTO recipe.Ingredients (ingredientName, calory)
VALUES
('Tomato', 18),
('Chicken Breast', 165),
('Pasta', 131),
('Olive Oil', 119),
('Garlic', 4),
('Basil', 1),
('Ground Beef', 250),
('Lettuce', 5),
('Parmesan Cheese', 431),
('Bread', 79);

-- Recipe_Ingredients
INSERT INTO recipe.Recipe_Ingredients (recipeID, ingredientID, quantity)
VALUES
(1, 3, 200),
(1, 7, 150),
(1, 4, 50),
(2, 2, 200),
(2, 8, 100),
(2, 9, 50),
(3, 10, 200),
(3, 5, 5),
(3, 6, 5),
(4, 1, 100),
(4, 4, 20),
(4, 5, 10),
(5, 9, 30),
(5, 10, 100),
(6, 2, 150),
(6, 8, 50),
(6, 6, 10),
(7, 1, 80),
(7, 4, 30),
(7, 5, 15);

-- RecipeEditQueue
INSERT INTO recipe.RecipeEditQueue (recipeID, editorID, oldDescription, newDescription, oldInstruction, newInstruction, isApproved)
VALUES
(1, 2, 'A classic Italian pasta dish', 'An improved classic Italian pasta dish', '1. Cook the pasta. 2. Prepare the sauce. 3. Mix and serve.', '1. Cook the pasta. 2. Prepare the sauce with extra garlic. 3. Mix and serve.', TRUE),
(2, 1, 'A healthy Caesar salad with grilled chicken', 'A healthier Caesar salad with grilled chicken', '1. Grill the chicken. 2. Prepare the salad. 3. Mix and serve.', '1. Grill the chicken. 2. Prepare the salad with extra lettuce. 3. Mix and serve.', TRUE),
(3, 3, 'A rich and moist chocolate cake', 'A richer and moister chocolate cake', '1. Prepare the batter. 2. Bake the cake. 3. Let it cool and serve.', '1. Prepare the batter. 2. Bake the cake with extra cocoa. 3. Let it cool and serve.', TRUE),
(4, 4, 'A quick and easy vegetable stir fry', 'A quicker and easier vegetable stir fry', '1. Prepare the vegetables. 2. Stir fry the vegetables. 3. Serve with rice.', '1. Prepare the vegetables. 2. Stir fry the vegetables with soy sauce. 3. Serve with rice.', TRUE),
(5, 2, 'Fluffy pancakes perfect for breakfast', 'Fluffier pancakes perfect for breakfast', '1. Prepare the batter. 2. Cook the pancakes. 3. Serve with syrup.', '1. Prepare the batter with extra eggs. 2. Cook the pancakes. 3. Serve with syrup.', TRUE);
	
-- IngredientEditQueue
INSERT INTO recipe.IngredientEditQueue (editID, recipeID, ingredientID, newQuantity, newIngredientName, newCalory)
VALUES
(1, 1, 3, 250, NULL, NULL),
(2, 2, 8, 150, NULL, NULL),
(3, 3, 10, 250, NULL, NULL),
(4, 4, 1, 120, NULL, NULL),
(5, 5, 2, 250, NULL, NULL),
(1, 1, 7, 180, NULL, NULL),
(2, 2, 9, 70, NULL, NULL),
(3, 3, 5, 10, NULL, NULL),
(4, 4, 4, 40, NULL, NULL),
(5, 5, 6, 20, NULL, NULL);

-- Bookmark
INSERT INTO recipe.Bookmark (userID, recipeID)
VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5),
(6, 6),
(7, 7),
(8, 8),
(9, 9),
(10, 10);

-- Rating
INSERT INTO recipe.Rating (userID, recipeID, rating)
VALUES
(1, 1, 5),
(2, 2, 4),
(3, 3, 5),
(4, 4, 4),
(5, 5, 5),
(6, 6, 4),
(7, 7, 5),
(8, 8, 4),
(9, 9, 5),
(10, 10, 4);