# -*- coding: utf-8 -*-
""" rwlock.py

    A class to implement read-write locks on top of the standard threading
    library.

    This is implemented with two mutexes (threading.Lock instances) as per this
    wikipedia pseudocode:

    https://en.wikipedia.org/wiki/Readers%E2%80%93writer_lock#Using_two_mutexes

    Code written by Tyler Neylon at Unbox Research.

    This file is public domain.
"""


# _______________________________________________________________________
# Imports

from contextlib import contextmanager
from threading import Lock


# _______________________________________________________________________
# Class

class RWLock(object):
    """ RWLock class; this is meant to allow an object to be read from by
        multiple threads, but only written to by a single thread at a time. See:
        https://en.wikipedia.org/wiki/Readers%E2%80%93writer_lock

        Usage:

            from rwlock import RWLock

            my_obj_rwlock = RWLock()

            # When reading from my_obj:
            with my_obj_rwlock.r_locked():
                do_read_only_things_with(my_obj)

            # When writing to my_obj:
            with my_obj_rwlock.w_locked():
                mutate(my_obj)
    """

    def __init__(self):
        """
        Initializes a new instance of the RWLock class.

        This constructor sets up the necessary locks for the RWLock object. It initializes the `w_lock` attribute to a
          new instance of the `Lock` class, the `num_r_lock` attribute to a new instance of the `Lock` class,
            and the `num_r` attribute to 0.

        Parameters:
            None

        Returns:
            None
        """

        self.w_lock = Lock()
        self.num_r_lock = Lock()
        self.num_r = 0

    # ___________________________________________________________________
    # Reading methods.

    def r_acquire(self):
        """
        Acquires a read lock on the RWLock object. Increments the number of read locks and acquires the write lock
          if this is the first read lock.

        This method does not take any parameters.

        This method does not return anything.
        """
        self.num_r_lock.acquire()
        self.num_r += 1
        if self.num_r == 1:
            self.w_lock.acquire()
        self.num_r_lock.release()

    def r_release(self):
        """
        Releases a read lock on the RWLock object. Decrements the number of read locks
         and releases the write lock if this is the last read lock.

        This method does not take any parameters.

        This method does not return anything.

        Raises:
            AssertionError: If the number of read locks is not greater than 0.
        """
        assert self.num_r > 0
        self.num_r_lock.acquire()
        self.num_r -= 1
        if self.num_r == 0:
            self.w_lock.release()
        self.num_r_lock.release()

    @contextmanager
    def r_locked(self):
        """ This method is designed to be used via the `with` statement. """
        try:
            self.r_acquire()
            yield
        finally:
            self.r_release()

    # ___________________________________________________________________
    # Writing methods.

    def w_acquire(self):
        """
        Acquire the write lock.

        This method acquires the write lock, preventing other threads from acquiring
        the write lock until the current thread has released it.

        Returns:
            None
        """
        self.w_lock.acquire()

    def w_release(self):
        """
        Release the write lock.

        This method releases the write lock that was previously acquired.

        Returns:
            None
        """
        self.w_lock.release()

    @contextmanager
    def w_locked(self):
        """ This method is designed to be used via the `with` statement. """
        try:
            self.w_acquire()
            yield
        finally:
            self.w_release()
