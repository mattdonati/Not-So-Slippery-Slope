import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as cx

def solid_plots(quarter, previous_quarter, solid_df, grid_df):

    solid_vmin = solid_df['solid_precip'].min()
    solid_vmax = solid_df['solid_precip'].max()

    data = solid_df.merge(grid_df, how='left', on='poly_index')
    data['geometry'] = gpd.GeoSeries.from_wkt(data['geometry'])
    data = gpd.GeoDataFrame(data, geometry='geometry')

    data = data.set_crs("EPSG:4326")
    data = data.to_crs("EPSG:3857")

    fig, axs = plt.subplots(1, 2, sharex='row', sharey='row')
    axs = axs.flatten()
    for ax in axs:
        ax.set_axis_off()

    data[(data['quarter'] == previous_quarter)].plot(ax=axs[0], column='solid_precip', alpha=.8, cmap='magma_r',
                                             vmin=solid_vmin, vmax=solid_vmax, legend=True, legend_kwds={
        "location":"bottom",
        "shrink":.75
    })
    cx.add_basemap(axs[0], source=cx.providers.Stamen.Toner)

    data[(data['quarter'] == quarter)].plot(ax=axs[1], column='solid_precip', alpha=.8, cmap='magma_r',
                                             vmin=solid_vmin, vmax=solid_vmax, legend=True, legend_kwds={
        "location":"bottom",
        "shrink":.75
    })
    cx.add_basemap(axs[1], source=cx.providers.Stamen.Toner)

    for ax in axs:
        txt = ax.texts[-1]
        txt.set_visible(False)

    fig.suptitle('Solid Precipitation', fontsize=10)
    axs[0].set_title(previous_quarter, fontsize=8)
    axs[1].set_title(quarter, fontsize=8)
    plt.subplots_adjust(wspace=0, hspace=0)
    return fig

def salt_plots(quarter, previous_quarter, salt_df, grid_df):

    salt_vmin = salt_df['salt'].min()
    salt_vmax = salt_df['salt'].max()

    data = salt_df.merge(grid_df, how='left', on='poly_index')
    data['geometry'] = gpd.GeoSeries.from_wkt(data['geometry'])
    data = gpd.GeoDataFrame(data, geometry='geometry')

    data = data.set_crs("EPSG:4326")
    data = data.to_crs("EPSG:3857")

    fig, axs = plt.subplots(1, 2,)
    axs = axs.flatten()
    for ax in axs:
        ax.set_axis_off()

    data[(data['quarter']== previous_quarter)].plot(ax=axs[0], column='salt', alpha=1, cmap='magma_r', vmin=salt_vmin,
                                                    vmax=salt_vmax, legend=True, legend_kwds={
        "location":"bottom",
        "shrink":.75
    })
    cx.add_basemap(axs[0], source=cx.providers.Stamen.Toner)

    data[(data['quarter'] == quarter)].plot(ax=axs[1], column='salt', alpha=1, cmap='magma_r',
                                             vmin=salt_vmin, vmax=salt_vmax, legend=True, legend_kwds={
        "location":"bottom",
        "shrink":.75
    })
    cx.add_basemap(axs[1], source=cx.providers.Stamen.Toner)

    for ax in axs:
        txt = ax.texts[-1]
        txt.set_visible(False)
    fig.suptitle('Estimated Market Salt Volume', fontsize=10)
    axs[0].set_title(previous_quarter, fontsize=8)
    axs[1].set_title(quarter, fontsize=8)
    return fig


def sales_growth(quarter, previous_quarter, predictions):
    predicted_sales = predictions[(predictions['quarter']==quarter)]['predicted'].iloc[0]/(2000*1000)
    prior_sales = predictions[(predictions['quarter']==previous_quarter)]['actual'].iloc[0]/(2000*1000)
    actual_sales = predictions[(predictions['quarter']==quarter)]['actual'].iloc[0]/(2000*1000)

    fig, ax = plt.subplots(layout='constrained')

    prior_rect = ax.bar(.5, prior_sales, .15, color='blue', label='Actual Volume')
    if predicted_sales > actual_sales:
        pred_rect = ax.bar(1, predicted_sales, .15, color='orange', alpha=1, label='Expected Volume')
        actual_rect = ax.bar(1, actual_sales, .15, color='blue', alpha=1)
    else:
        actual_rect = ax.bar(1, actual_sales, .15, color='blue', alpha=1)
        pred_rect = ax.bar(1, predicted_sales, .15, color='orange', alpha=1, label='Expected Volume')

    if actual_sales >= predicted_sales:
        actual_padding = 3
        predicted_padding = -15
        actual_color = 'blue'
        predicted_color='white'

    else:
        actual_padding = -15
        predicted_padding = 3
        actual_color = 'white'
        predicted_color = 'orange'
    ax.bar_label(prior_rect, padding=3, color='blue')
    ax.bar_label(actual_rect, padding=actual_padding, color=actual_color)
    ax.bar_label(pred_rect, padding=predicted_padding, color=predicted_color)

    ax.set_ylabel('Thousands of Tons')
    ax.set_title('Year Over Year Salt Volumes: Actual vs. Expected')
    ax.set_xticks((.5, 1),  (previous_quarter, quarter))
    ax.plot([.5, 1],[prior_sales, actual_sales], color='blue')
    ax.plot([.5, 1], [prior_sales, predicted_sales], color='orange')
    ax.legend(loc='upper left', ncols=2)
    ax.set_ylim(0, max(predicted_sales, actual_sales, prior_sales)*1.25)
    return fig


