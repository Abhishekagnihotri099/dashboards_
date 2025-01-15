from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.db.models import Q, Count, Sum, Case, When, IntegerField, FloatField, F
from backend_app.models import dsoutcome
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64

def filter_claim_leakage(request):
    # Extract query parameters
    filters = {
        'monitoring_date_start': request.GET.get('monitoring_date_start'),
        'monitoring_date_end': request.GET.get('monitoring_date_end'),
        'loss_date_start': request.GET.get('loss_date_start'),
        'loss_date_end': request.GET.get('loss_date_end'),
        'claim_closed_date_start': request.GET.get('claim_closed_date_start'),
        'claim_closed_date_end': request.GET.get('claim_closed_date_end'),
        'line_of_business': request.GET.getlist('line_of_business', []),
        'sub_line_of_business': request.GET.getlist('sub_line_of_business', []),
        'nature_of_loss': request.GET.getlist('nature_of_loss', []),
        'cause_of_loss': request.GET.getlist('cause_of_loss', []),
        'claim_status': request.GET.getlist('claim_status', []),
        'claim_state': request.GET.getlist('claim_state', []),
        'claim_consultant': request.GET.getlist('claim_consultant', []),
        'team': request.GET.getlist('team', []),
        'accurate_signal': request.GET.get('accurate_signal'),
        'brand': request.GET.getlist('brand', []),
        'compliance_category': request.GET.getlist('compliance_category', []),
        'parameter_name': request.GET.get('parameter_name'),
        'signal_status': request.GET.get('signal_status'),
        'manual_review': request.GET.get('manual_review'),
        'signal_reviewed_by': request.GET.get('signal_reviewed_by'),
    }
    print(filters)
    
    # Build query
    query = Q()
    if filters['monitoring_date_start'] and filters['monitoring_date_end']:
        query &= Q(claim__audits__audit_date__date__range=[filters['monitoring_date_start'], filters['monitoring_date_end']])
    if filters['loss_date_start'] and filters['loss_date_end']:
        query &= Q(claim__loss_date__range=[filters['loss_date_start'], filters['loss_date_end']])
    if filters['claim_closed_date_start'] and filters['claim_closed_date_end']:
        query &= Q(claim__close_date__range=[filters['claim_closed_date_start'], filters['claim_closed_date_end']])
    if filters['line_of_business']:
        query &= Q(lob__in=filters['line_of_business'])
    if filters['sub_line_of_business']:
        query &= Q(sub_line_of_business__in=filters['sub_line_of_business'])
    if filters['nature_of_loss']:
        query &= Q(nature_of_loss__in=filters['nature_of_loss'])
    if filters['cause_of_loss']:
        query &= Q(cause_of_loss__in=filters['cause_of_loss'])
    if filters['claim_status']:
        query &= Q(claim_status__in=filters['claim_status'])
    if filters['claim_state']:
        query &= Q(claim_state__in=filters['claim_state'])
    if filters['claim_consultant']:
        query &= Q(claim_consultant__in=filters['claim_consultant'])
    if filters['team']:
        query &= Q(team__in=filters['team'])
    if filters['accurate_signal']:
        query &= Q(accurate_signal=filters['accurate_signal'])
    if filters['brand']:
        query &= Q(brand__in=filters['brand'])
    if filters['compliance_category']:
        query &= Q(compliance_category__in=filters['compliance_category'])
    if filters['parameter_name']:
        query &= Q(parameter_name__icontains=filters['parameter_name'])
    if filters['signal_status']:
        query &= Q(signal_status=filters['signal_status'])
    if filters['manual_review']:
        query &= Q(manual_review=filters['manual_review'])
    if filters['signal_reviewed_by']:
        query &= Q(signal_reviewed_by=filters['signal_reviewed_by'])
    



    # Query with annotations
    claim_auditables = dsoutcome.objects.select_related(
        'claim', 
        'parameter'
    ).prefetch_related(
        'claim__dsoutcomes'
    ).filter(query).annotate(
        payout_calc=Case(
            When(
                claim__isnull=False,
                then=F('claim__paid_amount') + F('claim__remaining_reserve') - F('claim__total_recovery')
            ),
            default=0,
            output_field=FloatField()
        )
    )

    # Paginate
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 1000))
    start = (page - 1) * page_size
    end = start + 10000

    response_data = {
        'data': [
            {
                'claim_id': audit.claim.claim_id,
                'created_date': audit.created_date.strftime('%Y-%m-%d %H:%M:%S') if audit.created_date else None,
                'leakage_rate_final': audit.stored_leakage_rate_final,
                # 'leakage_rate_new': audit.stored_leakage_rate_new,
                'payout_amount': audit.payout_calc,
                'consultant_name': audit.consultant_name,
                'parameter_name': audit.parameter_name,
                'stored_final_leakage': audit.stored_leakage_rate_final,
                'stored_leakage_rate_new': audit.stored_leakage_rate_new,
                'stored_exclusions': audit.stored_exclusions,
                'leakage_category': audit.leakage_category,
                'leakage_type': audit.leakage_type,
                'lob': audit.lob,
                'pid' :  audit.parameter.stored_pid,
                'ai_signal': audit.ai_signal,
                'stored_ai_error_final': audit.stored_ai_error_final,
                'notification_comment' : audit.notification_comment
   
            }
            for audit in claim_auditables[start:end]
        ],
        'total_records': claim_auditables.count(),
        'page': page,
        'page_size': page_size,
    }
    return response_data


def generate_graphs(request):

    filtered_data = filter_claim_leakage(request)
    # print(filtered_data)
    filtered_data = filtered_data['data']
    df = pd.DataFrame(filtered_data)
    graphs = {}
    
    # Leakage Rate Trend
    fig = go.Figure()
    
    # Primary Y-axis - Bar charts
    fig.add_trace(go.Bar(
        x=df['created_date'],
        y=df['payout_amount'],
        name='Payout Amount'
    ))
    
    fig.add_trace(go.Bar(
        x=df['created_date'],
        y=df['leakage_rate_final'],
        name='Leakage Amount'
    ))
    
    # Secondary Y-axis - Line chart
    fig.add_trace(go.Scatter(
        x=df['created_date'],
        y=df['stored_leakage_rate_new'],
        name='Leakage Rate %',
        yaxis='y2',
        line=dict(color='red')
    ))
    
    fig.update_layout(
        title='Leakage Rate Trend',
        xaxis_title='Signal Generated Date',
        yaxis_title='Amount',
        yaxis2=dict(
            title='Leakage Rate %',
            overlaying='y',
            side='right'
        ),
        barmode='group'
    )
    
    graphs['leakage_trend'] = fig.to_json()

    # Convert to DataFrame and prepare date hierarchy
    df['year'] = pd.to_datetime(df['created_date']).dt.year
    df['month'] = pd.to_datetime(df['created_date']).dt.month
    
    # Calculate metrics by date
    opp_metrics = df.groupby('year').agg({
        'claim_id': 'nunique',  # Claims monitored
        'stored_exclusions': lambda x: len([i for i in x if i == 1])  # Opp identified
    }).reset_index()
    
    # Calculate ratio
    opp_metrics['opp_identified_ratio'] = (
        opp_metrics['stored_exclusions'] / opp_metrics['claim_id']
    ) * 100
    
    # Create Opportunity Trend Graph
    fig2 = go.Figure()
    
    # Bar charts for counts
    fig2.add_trace(go.Bar(
        x=opp_metrics['year'],
        y=opp_metrics['claim_id'],
        name='Claims Monitored'
    ))
    
    fig2.add_trace(go.Bar(
        x=opp_metrics['year'],
        y=opp_metrics['stored_exclusions'],
        name='Opportunities Identified'
    ))
    
    # Line chart for ratio
    fig2.add_trace(go.Scatter(
        x=opp_metrics['year'],
        y=opp_metrics['opp_identified_ratio'],
        name='Opportunity Identification Rate %',
        yaxis='y2',
        line=dict(color='red')
    ))
    
    fig2.update_layout(
        title='Opportunity Identification Trend',
        xaxis_title='Signal Generated Date',
        yaxis=dict(title='Count'),
        yaxis2=dict(
            title='Identification Rate %',
            overlaying='y',
            side='right'
        ),
        barmode='group'
    )
    
    graphs['opportunity_trend'] = fig2.to_json()
    # return graphs
    # Leakage by category pie with absolute values
    leakage_by_category = df.groupby('leakage_category')['leakage_rate_final'].sum().reset_index()
    
    # Add column for original values (for hover text)
    leakage_by_category['original_value'] = leakage_by_category['leakage_rate_final']
    
    # Use absolute values for pie chart
    leakage_by_category['leakage_rate_final'] = leakage_by_category['leakage_rate_final'].abs()
    
    # Create pie chart
    fig3 = go.Figure(data=[go.Pie(
        labels=leakage_by_category['leakage_category'],
        values=leakage_by_category['leakage_rate_final'],
        hole=.3,
        title='Leakage by Category',
        hovertemplate="<b>%{label}</b><br>" +
                     "Absolute Value: %{value:.2f}<br>" +
                     "Original Value: %{customdata:.2f}<extra></extra>",
        customdata=leakage_by_category['original_value'],
        marker=dict(
            colors=[
                'red' if val < 0 else 'blue' 
                for val in leakage_by_category['original_value']
            ]
        )
    )])
    
    fig3.update_layout(
        title='Leakage Distribution by Category (Absolute Values)',
        showlegend=True,
        annotations=[
            dict(
                text="Note: Red segments indicate negative values",
                showarrow=False,
                x=0,
                y=-0.2,
                xref="paper",
                yref="paper"
            )
        ]
    )
    
    graphs['leakage_category_pie'] = fig3.to_json()
    # Prepare hierarchical data
    # Create clean hierarchy with absolute values
    leakage_hierarchy = df.groupby(
        ['lob', 'leakage_category', 'leakage_type']
    )['leakage_rate_final'].agg(['sum', 'count']).reset_index()
    
    # Use absolute values but keep track of negatives
    leakage_hierarchy['is_negative'] = leakage_hierarchy['sum'] < 0
    leakage_hierarchy['abs_sum'] = leakage_hierarchy['sum'].abs()
    
    # Filter non-zero values
    leakage_hierarchy = leakage_hierarchy[leakage_hierarchy['abs_sum'] > 0]
    
    # Build hierarchy lists
    labels = []
    parents = []
    values = []
    colors = []
    
    # Add LOBs (Level 1)
    for lob in leakage_hierarchy['lob'].unique():
        if lob and not pd.isna(lob):
            lob_data = leakage_hierarchy[leakage_hierarchy['lob'] == lob]
            lob_sum = lob_data['sum'].sum()
            if abs(lob_sum) > 0:
                labels.append(lob)
                parents.append("")
                values.append(abs(lob_sum))
                colors.append('red' if lob_sum < 0 else 'blue')
    
    # Add Categories (Level 2)
    for lob in labels:
        lob_cats = leakage_hierarchy[leakage_hierarchy['lob'] == lob]
        for _, cat_row in lob_cats.iterrows():
            if cat_row['leakage_category'] and not pd.isna(cat_row['leakage_category']):
                if abs(cat_row['sum']) > 0:
                    labels.append(cat_row['leakage_category'])
                    parents.append(lob)
                    values.append(abs(cat_row['sum']))
                    colors.append('red' if cat_row['is_negative'] else 'blue')

    fig4 = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        marker=dict(
            colors=colors
        ),
        hovertemplate="<b>%{label}</b><br>" +
                     "Amount: %{value:,.2f}<br>" +
                     "Direction: %{customdata}<extra></extra>",
        customdata=['Negative' if c == 'red' else 'Positive' for c in colors]
    ))

    fig4.update_layout(
        title='Leakage Analysis Hierarchy (Red: Negative, Blue: Positive)',
        width=800,
        height=800
    )
    graphs['leakage_hierarchy'] = fig4.to_json()
    # Group data by consultant
    consultant_leakage = df.groupby('consultant_name')['leakage_rate_final'].sum().reset_index()
    
    # Create Treemap
    fig5 = go.Figure(go.Treemap(
        labels=consultant_leakage['consultant_name'],
        parents=[""] * len(consultant_leakage),  # Root level
        values=consultant_leakage['leakage_rate_final'],
        textinfo="label+value",
        marker=dict(
            colors=consultant_leakage['leakage_rate_final'],
            colorscale='RdBu',
            showscale=True
        ),
        hovertemplate='<b>%{label}</b><br>Leakage: %{value:.2f}<extra></extra>'
    ))

    fig5.update_layout(
        title='Leakage Distribution by Consultant',
        width=800,
        height=600
    )
    
    graphs['consultant_treemap'] = fig5.to_json()
    # return graphs
    # return JsonResponse(graphs)
    parameter_leakage = df.groupby(['pid'])['leakage_rate_final'].sum().reset_index()
# Create Bar Chart
    fig6 = go.Figure(go.Bar(
        x=parameter_leakage['pid'],
        y=parameter_leakage['leakage_rate_final'],
    
        hovertemplate=(
            '<b>Parameter ID:</b> %{x}<br>' +
            '<b>Leakage Amount:</b> %{y:.2f}<extra></extra>'
        )
    ))

    fig6.update_layout(
        title='Leakage Amount by Parameter',
        xaxis_title='Parameter ID',
        yaxis_title='Leakage Amount',
        showlegend=False,
        height=600,
        bargap=0.2
    )
    
    graphs['parameter_leakage'] = fig6.to_json()


    category_opportunities = df.groupby('leakage_category').agg({
        'claim_id': lambda x: len(set(x[df['stored_exclusions'] == 1]))  # Opp Identified formula
    }).reset_index()
    
    # Create pie chart
    fig6 = go.Figure(data=[go.Pie(
        labels=category_opportunities['leakage_category'],
        values=category_opportunities['claim_id'],
        hole=.3,
        title='Opportunities by Category'
    )])
    
    fig6.update_layout(
        title='Opportunity Distribution by Leakage Category',
        showlegend=True
    )
    
    graphs['opportunity_category_pie'] = fig6.to_json()

    # Prepare hierarchical data for opportunities
    opp_hierarchy = df.groupby(
        ['lob', 'leakage_category', 'leakage_type']
    ).agg({
        'claim_id': lambda x: len(set(x[df['stored_exclusions'] == 1]))
    }).reset_index()

    # Create Sunburst chart for opportunities
    fig7 = go.Figure(go.Sunburst(
        labels=opp_hierarchy['lob'].tolist() + 
               opp_hierarchy['leakage_category'].tolist() + 
               opp_hierarchy['leakage_type'].tolist(),
        parents=[""] * len(opp_hierarchy['lob'].unique()) +
                opp_hierarchy['lob'].tolist() +
                opp_hierarchy['leakage_category'].tolist(),
        values=opp_hierarchy['claim_id'].tolist() * 3,
        branchvalues="total",
        hovertemplate='<b>%{label}</b><br>Opportunities: %{value}<extra></extra>'
    ))

    fig7.update_layout(
        title='Opportunity Analysis by Business Hierarchy',
        width=800,
        height=800
    )

    graphs['opportunity_hierarchy'] = fig7.to_json()
    # Calculate opportunities by consultant
    consultant_opportunities = df.groupby('consultant_name').agg({
        'claim_id': lambda x: len(set(x[df['stored_exclusions'] == 1]))
    }).reset_index()
    
    # Create Treemap for consultant opportunities
    fig8 = go.Figure(go.Treemap(
        labels=consultant_opportunities['consultant_name'],
        parents=[""] * len(consultant_opportunities),
        values=consultant_opportunities['claim_id'],
        textinfo="label+value",
        marker=dict(
            colors=consultant_opportunities['claim_id'],
            colorscale='RdBu',
            showscale=True
        ),
        hovertemplate='<b>%{label}</b><br>Opportunities: %{value}<extra></extra>'
    ))

    fig8.update_layout(
        title='Opportunities Identified by Consultant',
        width=800,
        height=600
    )
    
    graphs['consultant_opportunities_treemap'] = fig8.to_json()

    # Group by parameter and calculate opportunities
    parameter_opportunities = df.groupby(['pid']).agg({
        'claim_id': lambda x: len(set(x[df['stored_exclusions'] == 1]))
    }).reset_index()
    
    # Create bar chart
    fig9 = go.Figure(go.Bar(
        x=parameter_opportunities['pid'],
        y=parameter_opportunities['claim_id'],
        hovertemplate=(
            '<b>Parameter ID:</b> %{x}<br>' +
            '<b>Opportunities:</b> %{y}<extra></extra>'
        )
    ))

    fig9.update_layout(
        title='Opportunities Identified by Parameter',
        xaxis_title='Parameter ID',
        yaxis_title='Opportunities Identified',
        showlegend=False,
        height=600,
        bargap=0.2
    )
    
    graphs['parameter_opportunities'] = fig9.to_json()

    # Group by consultant and calculate metrics
    consultant_ai_metrics = df.groupby('consultant_name').agg({
        'ai_signal': 'count',
        'stored_ai_error_final': 'mean'
    }).reset_index()
    
    # Create figure with secondary y-axis
    fig10 = go.Figure()
    
    # Add bars for AI signal count
    fig10.add_trace(go.Bar(
        x=consultant_ai_metrics['consultant_name'],
        y=consultant_ai_metrics['ai_signal'],
        name='AI Signal Count'
    ))
    
    # Add line for AI error final
    fig10.add_trace(go.Scatter(
        x=consultant_ai_metrics['consultant_name'],
        y=consultant_ai_metrics['stored_ai_error_final'],
        name='AI Error Final',
        yaxis='y2',
        line=dict(color='red', width=2)
    ))
    
    fig10.update_layout(
        title='AI Performance by Consultant',
        xaxis_title='Consultant Name',
        yaxis_title='AI Signal Count',
        yaxis2=dict(
            title='AI Error Final',
            overlaying='y',
            side='right'
        ),
        showlegend=True,
        height=600
    )
    
    graphs['consultant_ai_performance'] = fig10.to_json()

    # Prepare data for Sankey diagram
    # Prepare Sankey data - keep all values including zeros
    sankey_data = df.groupby(['notification_comment', 'leakage_category'])['leakage_rate_final'].sum().reset_index()
    
    # Create source and target mappings
    source_labels = sankey_data['notification_comment'].unique()
    target_labels = sankey_data['leakage_category'].unique()
    
    node_labels = list(source_labels) + list(target_labels)
    node_dict = {node: idx for idx, node in enumerate(node_labels)}
    
    # Create source, target, and value lists
    sources = [node_dict[row['notification_comment']] for _, row in sankey_data.iterrows()]
    targets = [node_dict[row['leakage_category']] + len(source_labels) for _, row in sankey_data.iterrows()]
    values = [abs(val) for val in sankey_data['leakage_rate_final']]  # Use absolute values for sizing
    
    # Create color mapping
    colors = ['rgba(255,0,0,0.6)' if val < 0 else 
              'rgba(163,169,169,0.4)' if val == 0 else 
              'rgba(0,0,255,0.6)' 
              for val in sankey_data['leakage_rate_final']]
    
    # Create Sankey diagram
    fig11 = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color="lightblue"
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors,
            hovertemplate=(
                'Source: %{source.label}<br>' +
                'Target: %{target.label}<br>' +
                'Value: %{customdata}<extra></extra>'
            ),
            customdata=[f"{val:.2f} ({'Negative' if val < 0 else 'Zero' if val == 0 else 'Positive'})" 
                       for val in sankey_data['leakage_rate_final']]
        )
    )])
    
    fig11.update_layout(
        title='Leakage Flow Analysis (Red: Negative, Gray: Zero, Blue: Positive)',
        font_size=10,
        height=1000,
        width=1200
    )
    
    graphs['leakage_flow_sankey'] = fig11.to_json()
    return JsonResponse(graphs)


