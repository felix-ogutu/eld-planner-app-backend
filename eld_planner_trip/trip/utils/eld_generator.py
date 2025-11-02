from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
import io
import os


class ELDGenerator:
    """Generate ELD Daily Log Sheets"""

    def __init__(self):
        self.page_width, self.page_height = landscape(letter)

    def generate_log(self, trip_id):
        """Generate ELD log PDF"""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=landscape(letter))

        self._draw_log_sheet(c, trip_id)

        c.save()

        # Save to file
        filename = f"eld_log_{trip_id}.pdf"
        filepath = os.path.join('media', 'logs', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'wb') as f:
            f.write(buffer.getvalue())

        return f"/media/logs/{filename}"

    def _draw_log_sheet(self, c, trip_id):
        """Draw ELD log sheet"""
        margin = 0.5 * inch

        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(margin, self.page_height - margin, "DRIVER'S DAILY LOG")

        # Date info
        c.setFont("Helvetica", 10)
        y_pos = self.page_height - margin - 0.3 * inch

        current_date = datetime.now().strftime("%m/%d/%Y")
        c.drawString(margin, y_pos, f"Date: {current_date}")
        c.drawString(margin + 3 * inch, y_pos, f"Trip ID: {trip_id}")

        # Draw grid
        self._draw_grid(c, margin, y_pos - 0.5 * inch)

        # Legend
        self._draw_legend(c, margin, margin)

    def _draw_grid(self, c, x_start, y_start):
        """Draw 24-hour grid"""
        grid_height = 4 * inch
        grid_width = 9 * inch

        c.setStrokeColorRGB(0.5, 0.5, 0.5)
        c.setLineWidth(0.5)

        statuses = ["OFF DUTY", "SLEEPER", "DRIVING", "ON DUTY"]
        row_height = grid_height / 4

        # Horizontal lines
        for i in range(5):
            y = y_start - (i * row_height)
            c.line(x_start, y, x_start + grid_width, y)

            if i < 4:
                c.setFont("Helvetica", 8)
                c.drawString(x_start + 0.1 * inch, y - row_height / 2, statuses[i])

        # Vertical lines
        hour_width = grid_width / 24
        for i in range(25):
            x = x_start + (i * hour_width)
            c.line(x, y_start, x, y_start - grid_height)

            if i % 2 == 0:
                c.setFont("Helvetica", 6)
                c.drawString(x - 0.05 * inch, y_start + 0.1 * inch, str(i))

        # Draw sample duty status
        self._draw_duty_status(c, x_start, y_start, grid_width, row_height)

    def _draw_duty_status(self, c, x_start, y_start, grid_width, row_height):
        """Draw duty status line"""
        c.setStrokeColorRGB(0, 0, 1)
        c.setLineWidth(2)

        hour_width = grid_width / 24

        # OFF DUTY (0-2 hours)
        y_off = y_start - (0.5 * row_height)
        c.line(x_start, y_off, x_start + 2 * hour_width, y_off)

        # DRIVING (2-13 hours)
        y_driving = y_start - (2.5 * row_height)
        c.line(x_start + 2 * hour_width, y_off, x_start + 2 * hour_width, y_driving)
        c.line(x_start + 2 * hour_width, y_driving, x_start + 13 * hour_width, y_driving)

        # ON DUTY (13-14 hours)
        y_on_duty = y_start - (3.5 * row_height)
        c.line(x_start + 13 * hour_width, y_driving, x_start + 13 * hour_width, y_on_duty)
        c.line(x_start + 13 * hour_width, y_on_duty, x_start + 14 * hour_width, y_on_duty)

        # Back to OFF DUTY
        c.line(x_start + 14 * hour_width, y_on_duty, x_start + 14 * hour_width, y_off)
        c.line(x_start + 14 * hour_width, y_off, x_start + 24 * hour_width, y_off)

    def _draw_legend(self, c, x_start, y_start):
        """Draw totals legend"""
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_start, y_start, "TOTAL HOURS:")

        c.setFont("Helvetica", 9)
        totals_x = x_start + 1.5 * inch
        c.drawString(totals_x, y_start, "OFF DUTY: 12.0")
        c.drawString(totals_x + 1.5 * inch, y_start, "SLEEPER: 0.0")
        c.drawString(totals_x + 3 * inch, y_start, "DRIVING: 11.0")
        c.drawString(totals_x + 4.5 * inch, y_start, "ON DUTY: 1.0")