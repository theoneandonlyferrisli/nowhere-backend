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

// ============================================
// SHARED CAROUSEL UTILITIES
// ============================================

const FALLBACK_BACKGROUNDS = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f6d365 0%, #fda085 100%)',
    'linear-gradient(135deg, #43cea2 0%, #185a9d 100%)'
];

const DEFAULT_FALLBACK_SLIDES = () => FALLBACK_BACKGROUNDS.map(bg => ({
    mode: 'fallback',
    fallback: bg
}));

// Utility function to log only in debug mode
function debugLog(...args) {
    if (CONFIG.FEATURES.DEBUG_MODE) {
        console.log(...args);
    }
}

// Function to build Firebase Storage URL
function getFirebaseStorageUrl(bucket, path, filename) {
    const encodedPath = encodeURIComponent(`${path}/${filename}`);
    return `https://firebasestorage.googleapis.com/v0/b/${bucket}/o/${encodedPath}?alt=media`;
}

// Function to collect all image URLs from multiple city folders
function getAllImageUrls() {
    const allUrls = [];
    
    CONFIG.CITY_IMAGES.forEach(city => {
        for (let i = 1; i <= city.count; i++) {
            const url = getFirebaseStorageUrl(CONFIG.FIREBASE_BUCKET, city.path, `${i}.jpg`);
            allUrls.push(url);
        }
    });
    
    // Shuffle if enabled
    if (CONFIG.CAROUSEL.SHUFFLE) {
        for (let i = allUrls.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [allUrls[i], allUrls[j]] = [allUrls[j], allUrls[i]];
        }
    }
    
    // Limit to MAX_PHOTOS
    return allUrls.slice(0, CONFIG.CAROUSEL.MAX_PHOTOS);
}

function getFallbackBackground(index) {
    return FALLBACK_BACKGROUNDS[index % FALLBACK_BACKGROUNDS.length];
}

// Function to preload image
function preloadImage(url) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(url);
        img.onerror = () => reject(new Error(`Failed to load image: ${url}`));
        img.src = url;
    });
}

// ============================================
// SHARED CAROUSEL INITIALIZATION
// ============================================

/**
 * Initialize carousel with async image loading and fallbacks
 * @param {string} containerId - ID of the carousel container element
 * @param {Object} options - Configuration options
 * @param {boolean} options.showDots - Whether to show navigation dots (default: false)
 * @param {string} options.dotsContainerId - ID of dots container if showDots is true
 * @param {string} options.loadingContainerId - ID of loading element to hide when ready
 * @returns {Promise<Object>} - Carousel control object with methods to control playback
 */
async function initCarousel(containerId, options = {}) {
    const {
        showDots = false,
        dotsContainerId = null,
        loadingContainerId = null
    } = options;
    
    try {
        debugLog('Initializing carousel...');
        
        const carouselContainer = document.getElementById(containerId);
        if (!carouselContainer) {
            console.error('Carousel container not found:', containerId);
            return null;
        }
        
        // Get all image URLs from configured city folders
        if (!CONFIG.CITY_IMAGES || CONFIG.CITY_IMAGES.length === 0) {
            debugLog('No carousel images configured; using fallbacks');
            return renderCarousel(carouselContainer, DEFAULT_FALLBACK_SLIDES(), {
                showDots,
                dotsContainerId,
                loadingContainerId
            });
        }

        const imageUrls = getAllImageUrls();
        
        if (imageUrls.length === 0) {
            debugLog('No images available; using fallbacks');
            return renderCarousel(carouselContainer, DEFAULT_FALLBACK_SLIDES(), {
                showDots,
                dotsContainerId,
                loadingContainerId
            });
        }
        
        debugLog('Image URLs:', imageUrls);
        
        // Preload all images and capture status
        const preloadPromises = imageUrls.map((url, index) =>
            preloadImage(url)
                .then(() => ({
                    mode: 'image',
                    url,
                    fallback: getFallbackBackground(index),
                    status: 'loaded'
                }))
                .catch(error => {
                    console.warn(`Carousel image failed to preload: ${url}`, error);
                    return {
                        mode: 'image',
                        url,
                        fallback: getFallbackBackground(index),
                        status: 'failed'
                    };
                })
        );

        const slidesData = await Promise.all(preloadPromises);

        const hasLoadedImage = slidesData.some(slide => slide.status === 'loaded');
        if (!hasLoadedImage) {
            console.warn('All carousel images failed to preload. Verify that images in Firebase Storage are publicly accessible.');
        }

        const carouselControl = renderCarousel(carouselContainer, slidesData, {
            showDots,
            dotsContainerId,
            loadingContainerId
        });
        
        debugLog('Carousel initialized successfully');
        return carouselControl;
        
    } catch (error) {
        console.error('Error initializing carousel:', error);
        
        const carouselContainer = document.getElementById(containerId);
        if (carouselContainer) {
            return renderCarousel(carouselContainer, DEFAULT_FALLBACK_SLIDES(), {
                showDots,
                dotsContainerId,
                loadingContainerId
            });
        }
        
        return null;
    }
}

/**
 * Render carousel slides and set up autoplay
 * @private
 */
function renderCarousel(carouselContainer, slidesData, options = {}) {
    const {
        showDots = false,
        dotsContainerId = null,
        loadingContainerId = null
    } = options;
    
    if (!Array.isArray(slidesData) || !slidesData.length) {
        console.error('Invalid slides data');
        return null;
    }
    
    const slides = slidesData.map(slide => ({ ...slide }));
    let currentSlide = 0;
    let autoplayInterval = null;
    
    // Clear existing content
    carouselContainer.innerHTML = '';
    
    // Create slides
    slides.forEach((slideData, index) => {
        const slide = document.createElement('div');
        slide.className = 'carousel-slide';
        
        if (slideData.mode === 'image') {
            const backgrounds = [];
            if (slideData.url) {
                backgrounds.push(`url(${slideData.url})`);
            }
            if (slideData.fallback) {
                backgrounds.push(slideData.fallback);
            }
            slide.style.backgroundImage = backgrounds.join(', ');
            if (slideData.status === 'failed') {
                slide.setAttribute('data-image-status', 'fallback');
            }
        } else {
            slide.style.backgroundImage = slideData.fallback;
        }
        
        if (index === 0) {
            slide.classList.add('active');
        }
        
        carouselContainer.appendChild(slide);
    });
    
    // Create dots if requested
    let dotsContainer = null;
    if (showDots && dotsContainerId) {
        dotsContainer = document.getElementById(dotsContainerId);
        if (dotsContainer) {
            dotsContainer.innerHTML = '';
            slides.forEach((_, index) => {
                const dot = document.createElement('div');
                dot.className = 'dot';
                if (index === 0) {
                    dot.classList.add('active');
                }
                dot.addEventListener('click', () => goToSlide(index));
                dotsContainer.appendChild(dot);
            });
        }
    }
    
    // Hide loading indicator if specified
    if (loadingContainerId) {
        const loading = document.getElementById(loadingContainerId);
        if (loading) {
            loading.classList.add('hidden');
        }
    }
    
    // Function to go to specific slide
    function goToSlide(index) {
        const allSlides = carouselContainer.querySelectorAll('.carousel-slide');
        const allDots = dotsContainer ? dotsContainer.querySelectorAll('.dot') : [];
        
        // Remove active class from current slide
        allSlides[currentSlide].classList.remove('active');
        if (allDots.length > 0) {
            allDots[currentSlide].classList.remove('active');
        }
        
        // Add active class to new slide
        currentSlide = index;
        allSlides[currentSlide].classList.add('active');
        if (allDots.length > 0) {
            allDots[currentSlide].classList.add('active');
        }
        
        // Preload next image if enabled
        if (CONFIG.CAROUSEL.PRELOAD_NEXT) {
            const nextIndex = (currentSlide + 1) % slides.length;
            const nextSlideData = slides[nextIndex];
            if (nextSlideData?.mode === 'image' && nextSlideData.url) {
                preloadImage(nextSlideData.url).catch(err => debugLog('Failed to preload next image', err));
            }
        }
    }
    
    // Function to go to next slide
    function nextSlide() {
        const nextIndex = (currentSlide + 1) % slides.length;
        goToSlide(nextIndex);
    }
    
    // Function to start autoplay
    function startAutoplay() {
        if (autoplayInterval) {
            clearInterval(autoplayInterval);
        }
        if (slides.length <= 1) {
            return;
        }
        autoplayInterval = setInterval(nextSlide, CONFIG.CAROUSEL.TRANSITION_DURATION);
    }
    
    // Function to stop autoplay
    function stopAutoplay() {
        if (autoplayInterval) {
            clearInterval(autoplayInterval);
            autoplayInterval = null;
        }
    }
    
    // Start autoplay
    startAutoplay();
    
    // Return control object
    return {
        goToSlide,
        nextSlide,
        startAutoplay,
        stopAutoplay,
        getCurrentSlide: () => currentSlide,
        getSlidesCount: () => slides.length
    };
}
