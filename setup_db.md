-- Insert Sample Data
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
(1, 1, 8.0), (1, 2, 7.0), (1, 3, 10.0), (1, 4, 4.0), (1, 5, 7.0), (1, 6, 8.0), (1, 7, 7.0), (1, 8, 9.0), (1, 9, 6.0), (1, 10, 8.0),
(2, 1, 9.0), (2, 2, 8.0), (2, 3, 6.0), (2, 4, 5.0), (2, 5, 6.0), (2, 6, 7.0), (2, 7, 8.0), (2, 8, 7.0), (2, 9, 4.0), (2, 10, 9.0),
(3, 1, 7.0), (3, 2, 9.0), (3, 3, 4.0), (3, 4, 6.0), (3, 5, 5.0), (3, 6, 8.0), (3, 7, 9.0), (3, 8, 4.0), (3, 9, 7.0), (3, 10, 6.0),
(4, 1, 10.0), (4, 2, 6.0), (4, 3, 8.0), (4, 4, 7.0), (4, 5, 4.0), (4, 6, 7.0), (4, 7, 9.0), (4, 8, 8.0), (4, 9, 6.0), (4, 10, 7.0),
(5, 1, 5.0), (5, 2, 7.0), (5, 3, 9.0), (5, 4, 6.0), (5, 5, 5.0), (5, 6, 8.0), (5, 7, 7.0), (5, 8, 9.0), (5, 9, 4.0), (5, 10, 6.0),
(6, 1, 6.0), (6, 2, 8.0), (6, 3, 7.0), (6, 4, 9.0), (6, 5, 4.0), (6, 6, 9.0), (6, 7, 7.0), (6, 8, 6.0), (6, 9, 8.0), (6, 10, 7.0),
(7, 1, 4.0), (7, 2, 10.0), (7, 3, 7.0), (7, 4, 8.0), (7, 5, 5.0), (7, 6, 6.0), (7, 7, 9.0), (7, 8, 8.0), (7, 9, 4.0), (7, 10, 9.0),
(8, 1, 7.0), (8, 2, 9.0), (8, 3, 5.0), (8, 4, 6.0), (8, 5, 8.0), (8, 6, 7.0), (8, 7, 8.0), (8, 8, 9.0), (8, 9, 6.0), (8, 10, 7.0),
(9, 1, 8.0), (9, 2, 5.0), (9, 3, 6.0), (9, 4, 9.0), (9, 5, 7.0), (9, 6, 6.0), (9, 7, 8.0), (9, 8, 9.0), (9, 9, 5.0), (9, 10, 8.0),
(10, 1, 7.0), (10, 2, 6.0), (10, 3, 8.0), (10, 4, 10.0), (10, 5, 5.0), (10, 6, 9.0), (10, 7, 7.0), (10, 8, 8.0), (10, 9, 6.0), (10, 10, 9.0);