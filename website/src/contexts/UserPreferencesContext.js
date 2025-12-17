import React, { createContext, useContext, useReducer, useEffect } from 'react';

// Initial state for user preferences
const initialState = {
  preferences: {
    learningPath: 'beginner', // beginner, intermediate, advanced
    interests: [],
    completedChapters: [],
    bookmarkedSections: [],
    preferredLanguage: 'en',
    accessibility: {
      fontSize: 'medium',
      highContrast: false,
      darkMode: null // null means follow system preference
    }
  },
  progress: {
    currentChapter: null,
    overallProgress: 0,
    timeSpent: 0 // in minutes
  }
};

// Actions
const SET_LEARNING_PATH = 'SET_LEARNING_PATH';
const ADD_INTEREST = 'ADD_INTEREST';
const REMOVE_INTEREST = 'REMOVE_INTEREST';
const MARK_CHAPTER_COMPLETED = 'MARK_CHAPTER_COMPLETED';
const MARK_CHAPTER_INCOMPLETE = 'MARK_CHAPTER_INCOMPLETE';
const ADD_BOOKMARK = 'ADD_BOOKMARK';
const REMOVE_BOOKMARK = 'REMOVE_BOOKMARK';
const SET_PREFERRED_LANGUAGE = 'SET_PREFERRED_LANGUAGE';
const UPDATE_ACCESSIBILITY = 'UPDATE_ACCESSIBILITY';
const UPDATE_PROGRESS = 'UPDATE_PROGRESS';
const SET_CURRENT_CHAPTER = 'SET_CURRENT_CHAPTER';

// Reducer
function preferencesReducer(state, action) {
  switch (action.type) {
    case SET_LEARNING_PATH:
      return {
        ...state,
        preferences: {
          ...state.preferences,
          learningPath: action.payload
        }
      };
    case ADD_INTEREST:
      if (!state.preferences.interests.includes(action.payload)) {
        return {
          ...state,
          preferences: {
            ...state.preferences,
            interests: [...state.preferences.interests, action.payload]
          }
        };
      }
      return state;
    case REMOVE_INTEREST:
      return {
        ...state,
        preferences: {
          ...state.preferences,
          interests: state.preferences.interests.filter(interest => interest !== action.payload)
        }
      };
    case MARK_CHAPTER_COMPLETED:
      if (!state.preferences.completedChapters.includes(action.payload)) {
        return {
          ...state,
          preferences: {
            ...state.preferences,
            completedChapters: [...state.preferences.completedChapters, action.payload]
          }
        };
      }
      return state;
    case MARK_CHAPTER_INCOMPLETE:
      return {
        ...state,
        preferences: {
          ...state.preferences,
          completedChapters: state.preferences.completedChapters.filter(chapter => chapter !== action.payload)
        }
      };
    case ADD_BOOKMARK:
      if (!state.preferences.bookmarkedSections.includes(action.payload)) {
        return {
          ...state,
          preferences: {
            ...state.preferences,
            bookmarkedSections: [...state.preferences.bookmarkedSections, action.payload]
          }
        };
      }
      return state;
    case REMOVE_BOOKMARK:
      return {
        ...state,
        preferences: {
          ...state.preferences,
          bookmarkedSections: state.preferences.bookmarkedSections.filter(section => section !== action.payload)
        }
      };
    case SET_PREFERRED_LANGUAGE:
      return {
        ...state,
        preferences: {
          ...state.preferences,
          preferredLanguage: action.payload
        }
      };
    case UPDATE_ACCESSIBILITY:
      return {
        ...state,
        preferences: {
          ...state.preferences,
          accessibility: {
            ...state.preferences.accessibility,
            ...action.payload
          }
        }
      };
    case SET_CURRENT_CHAPTER:
      return {
        ...state,
        progress: {
          ...state.progress,
          currentChapter: action.payload
        }
      };
    case UPDATE_PROGRESS:
      return {
        ...state,
        progress: {
          ...state.progress,
          ...action.payload
        }
      };
    default:
      return state;
  }
}

// Context
const UserPreferencesContext = createContext();

// Provider component
export function UserPreferencesProvider({ children }) {
  const [state, dispatch] = useReducer(preferencesReducer, initialState);

  // Load preferences from localStorage on initial render
  useEffect(() => {
    const savedPreferences = localStorage.getItem('userPreferences');
    if (savedPreferences) {
      try {
        const parsed = JSON.parse(savedPreferences);
        // Merge with initial state to ensure all properties exist
        const mergedState = {
          ...initialState,
          ...parsed,
          preferences: {
            ...initialState.preferences,
            ...parsed.preferences
          },
          progress: {
            ...initialState.progress,
            ...parsed.progress
          }
        };
        // Dispatch actions to update state
        Object.keys(mergedState.preferences).forEach(key => {
          if (key === 'learningPath') {
            dispatch({ type: SET_LEARNING_PATH, payload: mergedState.preferences[key] });
          } else if (key === 'interests') {
            mergedState.preferences[key].forEach(interest => {
              dispatch({ type: ADD_INTEREST, payload: interest });
            });
          } else if (key === 'completedChapters') {
            mergedState.preferences[key].forEach(chapter => {
              dispatch({ type: MARK_CHAPTER_COMPLETED, payload: chapter });
            });
          } else if (key === 'bookmarkedSections') {
            mergedState.preferences[key].forEach(section => {
              dispatch({ type: ADD_BOOKMARK, payload: section });
            });
          } else if (key === 'preferredLanguage') {
            dispatch({ type: SET_PREFERRED_LANGUAGE, payload: mergedState.preferences[key] });
          } else if (key === 'accessibility') {
            dispatch({ type: UPDATE_ACCESSIBILITY, payload: mergedState.preferences[key] });
          }
        });
        if (mergedState.progress.currentChapter) {
          dispatch({ type: SET_CURRENT_CHAPTER, payload: mergedState.progress.currentChapter });
        }
        dispatch({ type: UPDATE_PROGRESS, payload: mergedState.progress });
      } catch (error) {
        console.error('Error loading preferences from localStorage:', error);
      }
    }
  }, []);

  // Save preferences to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('userPreferences', JSON.stringify(state));
  }, [state]);

  // Helper functions
  const setLearningPath = (path) => {
    dispatch({ type: SET_LEARNING_PATH, payload: path });
  };

  const addInterest = (interest) => {
    dispatch({ type: ADD_INTEREST, payload: interest });
  };

  const removeInterest = (interest) => {
    dispatch({ type: REMOVE_INTEREST, payload: interest });
  };

  const markChapterCompleted = (chapterId) => {
    dispatch({ type: MARK_CHAPTER_COMPLETED, payload: chapterId });
  };

  const markChapterIncomplete = (chapterId) => {
    dispatch({ type: MARK_CHAPTER_INCOMPLETE, payload: chapterId });
  };

  const isChapterCompleted = (chapterId) => {
    return state.preferences.completedChapters.includes(chapterId);
  };

  const addBookmark = (sectionId) => {
    dispatch({ type: ADD_BOOKMARK, payload: sectionId });
  };

  const removeBookmark = (sectionId) => {
    dispatch({ type: REMOVE_BOOKMARK, payload: sectionId });
  };

  const isBookmarked = (sectionId) => {
    return state.preferences.bookmarkedSections.includes(sectionId);
  };

  const setPreferredLanguage = (language) => {
    dispatch({ type: SET_PREFERRED_LANGUAGE, payload: language });
  };

  const updateAccessibility = (accessibilitySettings) => {
    dispatch({ type: UPDATE_ACCESSIBILITY, payload: accessibilitySettings });
  };

  const setCurrentChapter = (chapterId) => {
    dispatch({ type: SET_CURRENT_CHAPTER, payload: chapterId });
  };

  const updateProgress = (progressData) => {
    dispatch({ type: UPDATE_PROGRESS, payload: progressData });
  };

  const value = {
    ...state,
    setLearningPath,
    addInterest,
    removeInterest,
    markChapterCompleted,
    markChapterIncomplete,
    isChapterCompleted,
    addBookmark,
    removeBookmark,
    isBookmarked,
    setPreferredLanguage,
    updateAccessibility,
    setCurrentChapter,
    updateProgress
  };

  return (
    <UserPreferencesContext.Provider value={value}>
      {children}
    </UserPreferencesContext.Provider>
  );
}

// Custom hook to use the context
export function useUserPreferences() {
  const context = useContext(UserPreferencesContext);
  if (!context) {
    throw new Error('useUserPreferences must be used within a UserPreferencesProvider');
  }
  return context;
}