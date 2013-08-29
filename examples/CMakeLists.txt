INCLUDE_DIRECTORIES ( .. )

ADD_EXECUTABLE(test_time test_time.c)
TARGET_LINK_LIBRARIES(test_time rtmd)

