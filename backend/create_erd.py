#!/usr/bin/env python3
"""
Script to generate an Entity Relationship Diagram for the Lagerverwaltung database
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

def create_erd():
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Colors
    table_color = '#E8F4FD'
    pk_color = '#FFE6CC'
    fk_color = '#E6F3E6'
    header_color = '#4A90E2'
    
    # Helper function to draw a table
    def draw_table(x, y, width, height, title, fields, pk_fields=None, fk_fields=None):
        pk_fields = pk_fields or []
        fk_fields = fk_fields or []
        
        # Main table rectangle
        table_rect = FancyBboxPatch((x, y), width, height,
                                    boxstyle="round,pad=0.02",
                                    facecolor=table_color,
                                    edgecolor='black',
                                    linewidth=1.5)
        ax.add_patch(table_rect)
        
        # Header
        header_rect = FancyBboxPatch((x, y + height - 0.6), width, 0.6,
                                     boxstyle="round,pad=0.02",
                                     facecolor=header_color,
                                     edgecolor='black',
                                     linewidth=1.5)
        ax.add_patch(header_rect)
        
        # Title
        ax.text(x + width/2, y + height - 0.3, title,
                ha='center', va='center', fontsize=12, fontweight='bold', color='white')
        
        # Fields
        field_height = (height - 0.6) / len(fields)
        for i, field in enumerate(fields):
            field_y = y + height - 0.6 - (i + 1) * field_height
            
            # Field background color
            if field.split()[0] in pk_fields:
                field_color = pk_color
            elif field.split()[0] in fk_fields:
                field_color = fk_color
            else:
                field_color = table_color
                
            field_rect = patches.Rectangle((x + 0.05, field_y + 0.05), 
                                         width - 0.1, field_height - 0.1,
                                         facecolor=field_color, alpha=0.7)
            ax.add_patch(field_rect)
            
            # Field text
            prefix = ""
            if field.split()[0] in pk_fields:
                prefix = "🔑 "
            elif field.split()[0] in fk_fields:
                prefix = "🔗 "
                
            ax.text(x + 0.1, field_y + field_height/2, prefix + field,
                    ha='left', va='center', fontsize=10)
    
    # Helper function to draw relationship lines
    def draw_relationship(x1, y1, x2, y2, label=""):
        ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2)
        
        # Arrow
        dx, dy = x2 - x1, y2 - y1
        length = np.sqrt(dx**2 + dy**2)
        dx_norm, dy_norm = dx/length, dy/length
        
        arrow_x = x2 - 0.2 * dx_norm
        arrow_y = y2 - 0.2 * dy_norm
        
        ax.annotate('', xy=(x2, y2), xytext=(arrow_x, arrow_y),
                   arrowprops=dict(arrowstyle='->', color='black', lw=2))
        
        # Label
        if label:
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mid_x, mid_y + 0.2, label, ha='center', va='center', 
                   fontsize=9, bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    # Draw tables
    
    # Lieferanten table
    draw_table(1, 8.5, 3, 2.5, 'LIEFERANTEN',
               ['id INTEGER PK', 'name TEXT NOT NULL', 'kontakt TEXT'],
               pk_fields=['id'])
    
    # Kunden table  
    draw_table(12, 8.5, 3, 2.5, 'KUNDEN',
               ['id INTEGER PK', 'name TEXT NOT NULL', 'kontakt TEXT'],
               pk_fields=['id'])
    
    # Artikel table
    draw_table(1, 5, 3.5, 3.5, 'ARTIKEL',
               ['artikelnummer TEXT PK', 'bezeichnung TEXT NOT NULL', 'lieferant_id INTEGER FK', 'mindestmenge INTEGER DEFAULT 1'],
               pk_fields=['artikelnummer'], fk_fields=['lieferant_id'])
    
    # Projekte table
    draw_table(12, 5, 3, 2.5, 'PROJEKTE',
               ['id INTEGER PK', 'projektname TEXT NOT NULL', 'kunde_id INTEGER FK'],
               pk_fields=['id'], fk_fields=['kunde_id'])
    
    # Lagerbestand table
    draw_table(6, 7, 4, 4, 'LAGERBESTAND',
               ['id INTEGER PK', 'artikelnummer TEXT FK', 'verfuegbare_menge INTEGER', 
                'einkaufspreis REAL', 'einlagerungsdatum TEXT'],
               pk_fields=['id'], fk_fields=['artikelnummer'])
    
    # Verkäufe table
    draw_table(6, 1.5, 4, 4, 'VERKÄUFE',
               ['id INTEGER PK', 'projekt_id INTEGER FK', 'artikelnummer TEXT FK',
                'verkaufte_menge INTEGER', 'verkaufspreis REAL', 'verkaufsdatum TEXT'],
               pk_fields=['id'], fk_fields=['projekt_id', 'artikelnummer'])
    
    # Draw relationships
    
    # Lieferanten -> Artikel
    draw_relationship(4, 9.5, 1, 6.5, '1:N')
    
    # Kunden -> Projekte  
    draw_relationship(12, 9.5, 15, 6.5, '1:N')
    
    # Artikel -> Lagerbestand
    draw_relationship(4.5, 6, 6, 9, '1:N')
    
    # Artikel -> Verkäufe
    draw_relationship(4.5, 5, 6, 3.5, '1:N')
    
    # Projekte -> Verkäufe
    draw_relationship(12, 5.5, 10, 3.5, '1:N')
    
    # Add title
    ax.text(8, 11.5, 'Lagerverwaltung - Datenmodell', ha='center', va='center',
           fontsize=18, fontweight='bold')
    
    # Add legend
    legend_x, legend_y = 0.5, 1.5
    ax.text(legend_x, legend_y + 1, 'Legende:', fontsize=12, fontweight='bold')
    
    # PK legend
    pk_rect = patches.Rectangle((legend_x, legend_y + 0.5), 0.3, 0.3, facecolor=pk_color)
    ax.add_patch(pk_rect)
    ax.text(legend_x + 0.4, legend_y + 0.65, '🔑 Primary Key', fontsize=10)
    
    # FK legend  
    fk_rect = patches.Rectangle((legend_x, legend_y), 0.3, 0.3, facecolor=fk_color)
    ax.add_patch(fk_rect)
    ax.text(legend_x + 0.4, legend_y + 0.15, '🔗 Foreign Key', fontsize=10)
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    fig = create_erd()
    plt.savefig('/Users/ikoerber/AIProjects/lagermgnt/backend/datenmodell.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    print("ER-Diagramm wurde als 'datenmodell.png' gespeichert")