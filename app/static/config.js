// Configuration for nowhere landing page
const CONFIG = {
    // App Information
    APP_NAME: 'nowhere',
    APP_TAGLINE: 'Explore. Discover. Share.',
    
    // Firebase Storage Configuration
    // Images will be loaded from multiple city folders
    // Format: https://firebasestorage.googleapis.com/v0/b/{bucket}/o/{path}?alt=media
    FIREBASE_BUCKET: 'steps-d1514.firebasestorage.app',
    
    // City folders to pull images from
    // Each entry should specify the city path and number of images available
    CITY_IMAGES: [
        {
            path: 'cities/new-york_new-york_us/featureImgsFullRes',
            count: 1  // Number of images (1.jpg through 5.jpg)
        },
        {
            path: 'cities/dubai_dubayy_ae/featureImgsFullRes',
            count: 1 
        },
        {
            path: 'cities/paris_ile-de-france_fr/featureImgsFullRes',
            count: 1 
        },
        {
            path: 'cities/sydney_new-south-wales_au/featureImgsFullRes',
            count: 1 
        },
        {
            path: 'cities/shanghai_shanghai_cn/featureImgsFullRes',
            count: 1 
        }
    ],
    
    // Carousel Settings
    CAROUSEL: {
        MAX_PHOTOS: 10,            // Maximum number of photos to show in carousel
        TRANSITION_DURATION: 5000, // Time between slides (milliseconds)
        PRELOAD_NEXT: true,        // Preload next image for smoother transitions
        SHUFFLE: true              // Randomize image order from different cities
    },
    
    // Features
    FEATURES: {
        DEBUG_MODE: false // Set to true to enable console logging
    }
};
