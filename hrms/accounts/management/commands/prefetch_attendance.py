import logging
from django.core.management.base import BaseCommand
from django.core.cache import cache
from accounts.models import Attendance

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Pre-fetch and cache attendance data for faster API responses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--page-size',
            type=int,
            default=20,
            help='Number of records to fetch per page (default: 20)'
        )
        parser.add_argument(
            '--pages',
            type=int,
            default=5,
            help='Number of pages to pre-fetch (default: 5)'
        )

    def handle(self, *args, **options):
        page_size = options['page_size']
        pages = options['pages']
        
        logger.info(f"Pre-fetching attendance data: {pages} pages of {page_size} records each")
        
        try:
            # Pre-fetch multiple pages of attendance data
            for page in range(1, pages + 1):
                self.prefetch_page(page, page_size)
                
            logger.info("Successfully pre-fetched attendance data")
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully pre-fetched {pages} pages of attendance data '
                    f'({page_size} records per page)'
                )
            )
        except Exception as e:
            logger.error(f"Error pre-fetching attendance data: {e}")
            self.stdout.write(
                self.style.ERROR(f'Error pre-fetching attendance data: {e}')
            )

    def prefetch_page(self, page, page_size):
        """Pre-fetch and cache a specific page of attendance data"""
        offset = (page - 1) * page_size
        
        # Get total count
        total_count = Attendance.objects.count()
        
        # Get paginated records
        attendance_records = Attendance.objects.all().order_by('-date')[offset:offset + page_size]
        
        result = []
        for record in attendance_records:
            result.append({
                "email": record.email.email,
                "role": record.email.role,
                "fullname": record.fullname,
                "department": record.department,
                "date": str(record.date),
                "check_in": str(record.check_in) if record.check_in else None,
                "check_out": str(record.check_out) if record.check_out else None,
                "check_in_photo": record.check_in_photo if record.check_in_photo else None,
                "check_out_photo": record.check_out_photo if record.check_out_photo else None,
            })
        
        # Calculate pagination info
        total_pages = (total_count + page_size - 1) // page_size
        
        response_data = {
            "attendance": result,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "total_count": total_count
            }
        }
        
        # Cache the result for 5 minutes
        cache_key = f"attendance_list_page_{page}_size_{page_size}"
        cache.set(cache_key, response_data, 60 * 5)  # Cache for 5 minutes
        
        logger.info(f"Pre-fetched and cached page {page} with {len(result)} records")