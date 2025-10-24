import React from 'react';
import styles from '../styles/Pagination.module.css';

const Pagination = ({
  currentPage,
  totalPages,
  totalItems,
  itemsPerPage,
  onPageChange,
  showInfo = true
}) => {
  const getPageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5;
    const halfVisible = Math.floor(maxVisiblePages / 2);

    let startPage = Math.max(1, currentPage - halfVisible);
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    return pages;
  };

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages && page !== currentPage) {
      onPageChange(page);
    }
  };

  const handlePrev = () => {
    handlePageChange(currentPage - 1);
  };

  const handleNext = () => {
    handlePageChange(currentPage + 1);
  };

  const handleFirst = () => {
    handlePageChange(1);
  };

  const handleLast = () => {
    handlePageChange(totalPages);
  };

  if (totalPages <= 1) {
    return null;
  }

  const pageNumbers = getPageNumbers();
  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);

  return (
    <div className={styles.pagination}>
      {showInfo && (
        <div className={styles.info}>
          Showing {startItem}-{endItem} of {totalItems} items
        </div>
      )}

      <div className={styles.controls}>
        <button
          className={styles.pageButton}
          onClick={handleFirst}
          disabled={currentPage === 1}
          title="First page"
        >
          ≪
        </button>

        <button
          className={styles.pageButton}
          onClick={handlePrev}
          disabled={currentPage === 1}
          title="Previous page"
        >
          ‹
        </button>

        {pageNumbers[0] > 1 && (
          <>
            <button
              className={styles.pageButton}
              onClick={() => handlePageChange(1)}
            >
              1
            </button>
            {pageNumbers[0] > 2 && <span className={styles.ellipsis}>…</span>}
          </>
        )}

        {pageNumbers.map(page => (
          <button
            key={page}
            className={`${styles.pageButton} ${page === currentPage ? styles.active : ''}`}
            onClick={() => handlePageChange(page)}
          >
            {page}
          </button>
        ))}

        {pageNumbers[pageNumbers.length - 1] < totalPages && (
          <>
            {pageNumbers[pageNumbers.length - 1] < totalPages - 1 && (
              <span className={styles.ellipsis}>…</span>
            )}
            <button
              className={styles.pageButton}
              onClick={() => handlePageChange(totalPages)}
            >
              {totalPages}
            </button>
          </>
        )}

        <button
          className={styles.pageButton}
          onClick={handleNext}
          disabled={currentPage === totalPages}
          title="Next page"
        >
          ›
        </button>

        <button
          className={styles.pageButton}
          onClick={handleLast}
          disabled={currentPage === totalPages}
          title="Last page"
        >
          ≫
        </button>
      </div>
    </div>
  );
};

export default Pagination;